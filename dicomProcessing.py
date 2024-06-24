from imports import * #import libraries from seperate imports.py file (needs to be in same directory as current)
from utilities import * #import functions from seperate utilities.py file (needs to be in same directory as current)

#input folders and filenames
replacedWordsFile = 'reportText_replacedWords.csv'
pathDirectoryOutputFile = 'paths.csv'
csvSaveDirectory = os.path.join(os.getcwd(), 'CSV Files')
nlpPredictionsFile = 'nlpPredictions.csv'

#outputFolders
allDataFile = 'allDataWithPredictions.csv'
errorData = 'errorData.csv'

#\\storage1.ris.wustl.edu\amlai\Active\Shared\Data\MIMIC 4\MIMIC-IV Chest XRays\physionet.org\files\mimic-cxr\2.0.0\files
imagesDir = input("Please provide the file path of the MIMIC CXR dicom files. Path should end in \\mimic-cxr\\2.0.0\\files" + '\n' +
              'example: \\networkDrive\\Users\\User1\\Data\\MIMIC 4\\MIMIC-IV Chest XRays\\physionet.org\\files\\mimic-cxr\\2.0.0\\files' 
                  + '\n')
while not os.path.exists(imagesDir) or imagesDir[-11:] != '2.0.0\\files':
    if os.path.exists(imagesDir) == False:
        print('\'' + imagesDir + '\'' + ' does not exist.')
    elif imagesDir[-11:] != '2.0.0\\files':
        print('\'' + imagesDir + '\'' + 'does not end in: \\2.0.0\\files') 
    imagesDir = input("Please provide the location of the mimic-cxr-reports.zip. You may type 'stop' to terminate." + '\n')
    if imagesDir == 'stop':
        raise Exception('Program terminated by user.')
        
#allFiles_ettPredictions was made in allFileProcessing
df_all=pd.read_csv(os.path.join(csvSaveDirectory, nlpPredictionsFile))
df_all['dicomDir']= df_all['dir'].apply(lambda x:joinPath(x, imagesDir = imagesDir))
df_all = df_all[['id', 'dir', 'dicomDir', 'ett', 'carinaDist(cm)']]

print('Processing DICOM headers for the entire database. This will likely take hours depending on equipment used.')
print('Progress bar will update every 1000 images.')
ret, errors = getDICOM_data(df_all)

tempDF = pd.DataFrame(ret)
dicomDataDF = pd.merge(tempDF,df_all[['id', 'ett', 'carinaDist(cm)']], on = 'id', how='inner', validate = 'm:1')
dicomDataDF.reset_index(drop = True, inplace = True)

print('Saving list of dicom images that could not be opened with current pydicom version to: ' + str(os.path.join(csvSaveDirectory, errorData)))
#List of dicom images that could not be opened by pydicom
errorDF = pd.DataFrame.from_dict(errors, orient='index')
errorDF.reset_index(level=None, inplace=True)
errorDF.rename(columns={'index':'file', 0:'id'}, inplace=True)
errorDF.to_csv(os.path.join(csvSaveDirectory, errorData),index=False)

#Filter down allDF to just values we want
views = ['AP', 'PA']
color = ['MONOCHROME2']
#ett = ['yes', 'no', 'unk']
print('Filtering non-AP/PA images and inverted images...')
filteredDF = dicomDataDF.loc[(dicomDataDF['view'].isin(views)) & (dicomDataDF['color'].isin(color))].copy()
filteredDF.reset_index(level=None, inplace = True, drop=True)
        
#Use the function getLowestSeries to find what images to keep with the lowest series value
#error list collects instances where the series number is the same for multiple images in the same study
print('Filtering studies with multiple images to the image with the lowest series...')
lowestSeries, errList = getLowestSeries(filteredDF)

#getLowestSeries looks at the instances where there are multiple images for one text file returns a dictionary with the id, file, and series of the image with the lowest series number
#How lowest series is laid out: lowestSeries = ['id':[p10***\s50***.txt, ...], 'file':[456-xxx--xxx.dcm, ...], 'series': [1,1,4,...]]
#I probably could have done this better but hind sight is 20/20

lowestDF = pd.DataFrame(lowestSeries) #convert the dictionary to a dataframe
seriesDF = pd.merge(lowestDF, filteredDF, on = ['id', 'file', 'series'], how='left') #have to get the other columns that correspond to that image from filtered DF. Because most cases are just a single image per report, there is only about 20,000 images with multiple series
filteredDF.drop_duplicates(subset=['id'], keep=False, inplace=True) #now drop all the filteredDF duplicates (of note, some duplicates have the same series number, which is caught my errList above. If you try to look at the numbers of dropped duplicates, and added back images it won't be perfectly equal)
finalDF = finalDF = pd.concat([filteredDF, seriesDF]) #now append the seriesDF from above #now append the seriesDF from above
finalDF.reset_index(level=None, inplace = True, drop=True)

def re_id(iD):
    newID = iD.split('\\')
    newID = newID[0] + '_' + newID[1][0:-4]
    return newID

finalDF['id'] = finalDF['id'].apply(re_id)
finalDF = finalDF[['file', 'dicomDir', 'id', 'ett', 'carinaDist(cm)']].copy()
finalDF.loc[finalDF['ett'].isna(), 'ett'] = 'no' #set all ett predictions that aren't classified to no

print('Saving final data file to: ' + str(os.path.join(csvSaveDirectory, allDataFile)))
finalDF.to_csv(os.path.join(csvSaveDirectory, allDataFile),index=False)