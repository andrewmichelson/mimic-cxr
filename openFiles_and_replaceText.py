#!/usr/bin/env python
# coding: utf-8

# Import necessary packages. This requires imports.py to be available.
print('Importing libraries...')
from imports import * #import libraries from seperate imports.py file (needs to be in same directory as current)

# Obtain directory information regarding the .zip file location from user input.

# Ask the user if the .zip file is in the current directory.
useCurrentDir = str
while useCurrentDir != 'n' and useCurrentDir != 'y':
    useCurrentDir = str.lower(input("Is mimic-cxr-reports.zip file in current directory? (Y/N)" + '\n' + 'Current Directory: ' + str(os.getcwd()) + '\n'))
    if useCurrentDir == 'y':
        zipDir = os.getcwd()
    elif useCurrentDir == 'n':
        # If not in the current directory, prompt the user to provide the location.
        zipDir = input("Please provide the location of the mimic-cxr-reports.zip." + '\n')
        while not os.path.exists(zipDir):
            print('\'' + zipDir + '\'' + ' does not exist.')
            zipDir = input("Please provide the location of the mimic-cxr-reports.zip. You may type 'stop' to terminate." + '\n')
            if zipDir == 'stop':
                raise Exception('Program terminated by user.')
    else:
        print('That was not a recognized answer.')

# Ask the user if they are using the default file name "mimic-cxr-reports.zip".
useFileName = str
while useFileName != 'n' and useFileName != 'y':
    useFileName = str.lower(input("Are you using the default file name, \"mimic-cxr-reports.zip\"? (Y/N)" + '\n'))
    if useFileName == 'y':
        zipFileName = 'mimic-cxr-reports.zip'
    elif useFileName == 'n':
        # If not, prompt the user to provide the file name.
        zipFileName = input("Please provide the file name of the zip file." + '\n')
        tempPath = os.path.join(zipDir, zipFileName)
        while not os.path.isfile(tempPath):
            print('\'' + zipFileName + '\'' + ' does not exist.')
            zipFileName = input("Please provide the file name of the zip file. You may type 'stop' to terminate." + '\n')
            tempPath = os.path.join(zipDir, zipFileName)
            if zipFileName == 'stop':
                raise Exception('Program terminated by user.')
    else:
        print('That was not a recognized answer.')

# Set up file and folder paths.
zipPath = os.path.join(zipDir, zipFileName)
extractFolder = os.path.join(os.getcwd(), 'Zip_Extraction')
if not os.path.exists(extractFolder):
    os.mkdir(extractFolder)
csvSaveDirectory = os.path.join(os.getcwd(), 'CSV Files')
if not os.path.exists(csvSaveDirectory):
    os.mkdir(csvSaveDirectory)
pathDirectoryOutputFile = 'paths.csv'
txtFileOutputName = 'reportText_replacedWords.csv'

# Unzip the file.
print('Unzipping...unzipping all files will take around 15 minutes.')
with ZipFile(zipPath, 'r') as z:
    z.extractall(extractFolder)
print('Unzipping complete.')

# Iterate through the directories of the files and create a dictionary with the path names.
res = []
i0 = os.path.join(extractFolder, 'files')  # Initializing data path
i1s = os.listdir(i0)

print("Building path directory...")
for i, i1 in enumerate(i1s):
    i2s = os.listdir('\\'.join([i0, i1]))
    
    print('Processing file folder {} out of {} ({:.1%})'.format(i + 1, len(i1s), (i + 1) / len(i1s)), end='\r', flush=True)

    for i2 in i2s:
        txts = os.listdir('\\'.join([i0, i1, i2]))
        
        for txt in txts:
            res.append([i0, i1, i2, txt, '\\'.join([i0, i1, i2, txt])])

# Save the paths to a CSV file.
df_paths = pd.DataFrame(res, columns=['i0', 'i1', 'i2', 'file_name', 'merged_path'])
print('\nSaving paths directory to: ' + str(csvSaveDirectory))
df_paths.to_csv(os.path.join(csvSaveDirectory, pathDirectoryOutputFile), index=False)

# Find ETT word equivalents and replace with ##ett##
# Only need to run once and then can load the CSV.

print('Finding instances of the word ETT in all text...')
df_paths = pd.read_csv(os.path.join(csvSaveDirectory, pathDirectoryOutputFile))
files = df_paths.merged_path.tolist()

filtering='!\"#%&\\\'()*<>?[]/' # no-meaning symbols
res=[]
#\b....\b denotes a perfect match for the letters between the b's 
#Had to use double \\ because python interputs a single \ as a negation unless you write an r before the string like 
#this r'something something'.The r denotes rich text and you cant pass rich text 
#have to use negative look behinds(?<!) and negative look aheads (?!) around just the word ett becuase ##ett## gets matched for /bett/b in the regex. See later functions for explination on lookahead and lookbehinds
names = ["\\bendotracheal tube\\b", "\\bet tube\\b", "\\bet-tube\\b", "\\bendotracheal-tube\\b", "(?<!##)\\bett\\b(?!##)", "\\bendotracheal\\b"] #endotracheal by itself has to be last! otherwise will change endotracheal tube to ##ett## tube and look weird

# Loop over all files.
for i, file in enumerate(files):
    if not i % 1000: 
        print('Processing file {} out of {} ({:.1%})'.format(i, len(files), (i / len(files))), end='\r', flush=True)
        
    with open(file) as f:
        txt = f.read().strip().lower().replace('\n', ' ').replace('\t', ' ')  # Read and clean the text.

    # Replace matched words with ##ett##.
    for word in names:
        if re.search(word, txt):
            txt = re.sub(word, '##ett##', txt)
            res.append([file, word, txt])

print('Processing file {} out of {} ({:.1%})'.format(i, len(files), (i / len(files))))

# Save the converted text data to a CSV file.
print('Saving converted text data to: ' + os.path.join(csvSaveDirectory, txtFileOutputName))
df_res = pd.DataFrame(res, columns=['file', 'word', 'text'])
df_res.to_csv(os.path.join(csvSaveDirectory, txtFileOutputName), index=False)