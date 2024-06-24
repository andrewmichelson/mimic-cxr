from imports import *

#Function to get the last two parts of the filename path to use as unique identifer  the full pathname
#example: 'C:\Users\ryan.mcguire\Documents\ETT Project\Data\files\p10\p10XXXXXX\s########.txt'
#example: this function will return 'p10XXXXXX\\s########.txt'
def getPathID(path):
    path = pathlib.Path(path) #convert the passed "path" to an actual path as it is passed as a string
    
    #with pathlib, you can use "parents" which is a list of all the subdirectories from deepest directory to root
    #the pathlib function "name" just displays the text of whatever you call
    #Example: parent[0] is p10XXXXX of 'C:\Users\ryan.mcguire\Documents\ETT Project\Data\files\p10\p10XXXXXX\s########.txt'
    #         parent[1] is p10, etc
    #if you call just "name" it displays the filename
    #So join the name of the last subdirectory with the name of the filename and return it    
    ret = path.parents[0].name + '\\' + path.name 
    
    return ret

def joinPath(txt, imagesDir = str):
    splitTxt = txt.split('\\')[-3:]
    imgSplit = imagesDir.split('\\')
    joinList = imgSplit+splitTxt
    return '\\'.join(joinList)

#For radiology reports with a formal impression that contains ##ett## in the impression, extract the impression
def getImpression(txt):
    #find impression with either a capital or lowercase 'I' where ##ett## is after it ((?=***) is a look ahead) and then get 0 to indefinite
    #characters (.*) to the end of the text ($)
    ret = re.findall(r'[iI]mpression(?=.*##ett##).*$', txt) 
    
    if len(ret) >1:
        return ret
    elif len(ret) == 0:
        return 'no impression'
    else:
        return ret[0]
    
#Remove is, the a, etc..
def removeArticles(txt):
    articles = ['\\bis\\b', '\\bthe\\b', '\\ba\\b']
    
    for article in articles:
        txt = re.sub(article, '', txt)
        txt = re.sub('  ', ' ', txt)
    
    return txt


def replaceDimensions(txt):
    #Replace centimeters to cm and millimeters to mm in case it is spelled out completely somewhere
    #the ?(question mark) says to match the previous pattern (in this case [s]) zero or one times
    txt = re.sub(r'\bcentimeter[s]?\b', 'cm', txt)
    txt = re.sub(r'\bmillimeter[s]?\b', 'mm', txt)
    return txt

def isMultiple(column):
    #If the passed variable is a list return a 1 otherwise return 0
    if isinstance(column,list):
        return 1
    else:
        return 0
    
#if a list is passed to the function, only keep the first value
#Otherwise return the value
def keepFirst(column):
    if isinstance(column,list):
        return column[0]
    else:
        return column

#Are there removal statements in the text passed to this function
#If yes, return 1
#if no, return 0
#how to test: df_ett.loc[(df_ett['text'].str.contains(r'##ett##(?=[^\.?!:;]*remov)')), 'text'] #looks for removal after
#how to test: df_ett.loc[(df_ett['text'].str.contains(r'remov(?=[^\.?!:;]*##ett##)')), 'text'] #looks for removal before ett
#Fancier test - > actually capture the search criteria. Since findall makes list, just make one giant list, convert that to a series, and use value_counts
# test = df_ett.loc[df_ett['text'].str.contains(r'##ett##(?=[^\.?!:;]*remov)[^\.?!:;]*'), 'text'].apply(lambda x:re.findall(r'##ett##(?=[^\.?!:;]*remov)[^\.?!:;]*', x))
# tstList = []
# for x in test:
#     for y in x:
#         tstList.append(y)
# pd.Series(tstList).value_counts()
def isRemoved(txt):
    
    #First, find ##ett## then look ahead and make sure there isn't any punctuation. (^) means NOT so ([^\.!?:;] means not any of these chacters. (\.) is an escaped period
    #need '*' after [^\.!?:;] because this allows the search engine to match 0 to infinite amount of the group preceeding it (so match infinite number of non puncuation characters). 
    #This way "a ##ett## that has been removed" will still be matched
    if re.findall(r'##ett##(?=[^\.?!:;]*remov)', txt): 
        return 1
    elif re.findall(r'remov(?=[^\.?!:;]*##ett##)', txt):
        return 1
    else:
        return 0
    
#Are there insertion statements in the texted passed
#yes = 1, no = 0
#how to test: df_ett.loc[df_ett['text'].str.contains(r'interval place(?=[^\.?!:;]*##ett##)')
#Fancier test - > actually capture the search criteria. Since findall makes list, just make one giant list, convert that to a series, and use value_counts
# test = df_ett.loc[df_ett['text'].str.contains(r'##ett##(?=[^\.?!:;]*insert)(?![^\.?!:;]*remov)'), 'text'].apply(lambda x:re.findall(r'##ett##(?=[^\.?!:;]*insert)(?![^\.?!:;]*remov)[^\.?!:;]*insert.{0,10}', x))
# tstList = []
# for x in test:
#     for y in x:
#         tstList.append(y)
# pd.Series(tstList).value_counts()
def isInserted(txt):
    #First, find ##ett##. then look ahead and make sure there isn't any punctuation. (^) means NOT so ([^\.!?:;] means not any of these chacters. (\.) is an escaped period
    #need '*' after [^\.!?:;] because this allows the search engine to match 0 to infinite amount of the group preceeding it (so match infinite number of non puncuation characters). 
    #This way "a ##ett## that has been placed" will still be matched
    #if no punction, then look literally for 'has been place'. If that matches then look and make sure the word "into" dosent follow place (or placed, [d]? means match 0 or 1 lowercase 'd')
    #if all conditions met, then return 1
    #Had to look for into afterwords because one text says "ett has been placed into the right mainstem)
    #Had to look for remove because some examples of "ett removed and tracheostomy tube has been placed", which this would catch
    if re.findall(r'##ett##(?=[^\.!?:;]*has been place)(?![^\.!?:;]*place[d]? into)(?![^\.!?:;]*remov)', txt):
        return 1
    #look for insertion but had to make sure remove was not in the same sentence. 
    elif re.findall(r'##ett##(?=[^\.?!:;]*insert)(?![^\.?!:;]*remov)', txt):
        return 1
    elif re.findall(r'interval place(?=[^\.?!:;]*##ett##)', txt): 
        return 1
    else:
        return 0
    
#Very simple. if the word tracheostomy or trach is in the text, return 1
def isTrach(txt):
    
    if re.search('tracheostomy', txt):
        return 1
    elif re.search(r'\btrach\b', txt):
        return 1
    else:
        return 0
    
def getCarinaDistance(txt):
    #Gets carina distance in centimeters
    #Very tricky regex - > return value is a list with (digit, unit) ex (5.5, cm) because of grouping
    #first look for ##ett##
    #Now look forward (?=...) and make sure there isn't any punctuation. (^) means NOT so ([^\.!?:;\d] means not any of these chacters. (\.) is an escaped period. \d is any digit
    #need '*' after [^\.!?:;] because this allows the search engine to match 0 to infinite amount of the group preceeding it (so match infinite number of non puncuation characters or digits).
    #also included \d in [^\.!?:;\d] because unlike isInserted/removed above, when we reach a digit, we want it to move foward with the pattern checking. 
        #very important here that a * will jump to the first character that fails the pattern and then backtraces from there. Use debugging with regex101 to better understand 
    #Then look for this pattern.(\d+\.\d+|\.\d+|\d+). Parenthesis are for groups and allow the use of logic. So find 1-infinite digits followed by a period (\.) and then 1-infinite more digits OR a period(.) followed by 1-infinite digits OR find 1-infinite digits
            #Made all the OR statements vs using (\d*\.\d*|\d+) because there were a few examples like "##ett## is approx. 5 cm from carina" where the periord(.) before 5 in this sentence 
            #was captured but not the nubmer 5. With all the OR statements, this example sentence actually fails now but if I made a case to fix this it would cause overfitting I felt like 
    #[\s\-\d\.]* =  match 0-infinite white space (\s), dashs (\-), or digits. This is because some of the text has carina ranges like 5.5-6.0mm from the carina
    #([cm]m) = match a 'c' or 'm' in the brackets (just one in this case because no * or + afterwords) followed by an m. So capture cm or mm. Don't need to look for centi/millimeters because I already converted all those words to cm/mm in a different function
    #([cm]m) = whole thing in parenthesis so this is the second group returned 
    #[^\.?!:;\d]*carina = match 0-infinite characters not included in the brackets (remeber ^ is a negation sympom) follwed by the actual word carina
    #Finally, because we are using grouping, findall will only return the result of the group. So in this case it will only return the decimals which we want
    #(?:...) -> Just FYI, if you want to use logic but not capture a group, use ?: inside the group. Ex -> (?:\d*\.\d*|\d+)
    
    #How to test
    #txt = 'chest: ##ett## tube has been slightly withdrawn in the interval, now terminating approximately 5.5mm from the carina. a dobbhoff'
    #re.findall(r'##ett##(?=[^\.?!:;\d]*((\d+\.\d+|\.\d+|\d+)[\s\-\d\.]*([cm]m)[^\.?!:;\d]*carina)', txt)
    
    #result 1 is used when there is a single distance such as "the ett is 6cm from the carina)
    #result 2 is used when there is a range of distances used, such as "the ett is 6-7cm from the carina)
    result1 = re.findall(r'##ett##(?=[^\.?!:;\d]*(\d+\.\d+|\.\d+|\d+)[\s]*([cm]m)[^\.?!:;\d]*carina)', txt) #did it this way to so I only had to process findall once, given i needed the len several times
    result2 = re.findall(r'##ett##(?=[^\.?!:;\d]*(\d+\.\d+|\.\d+|\d+)(?:and|to| |-)+(\d+\.\d+|\.\d+|\d+)[\s]*([cm]m)[^\.?!:;\d]*carina)', txt)
    if len(result1) >0:
        #used ret[-1] to get the last group in the list because some text may have the carina distance in the findings and impressions and findall will then return multiple values
        #so return the last group in the list which is likely the impression if there is an impression in the text
        #example return: [('5.5', 'cm'), ('5.5', 'cm'), ('5.4', 'cm')]
        if result1[-1][1] == 'mm': #ret[-1][1] is the unit
            try: 
                float(result1[-1][0])/10
            except:
                print("error")
                print(txt)
            else:
                ret = float(result1[-1][0])/10
            return ret
        else:
            try:
                float(result1[-1][0])
            except:
                print("error")
                print(txt)
            else:
                return float(result1[-1][0])
    elif len(result2) == 1:
            avgDist = (float(result2[0][0]) + float(result2[0][1]))/2
            if result2[0][2] == 'mm':
                avgDist = avgDist/10
            return avgDist
    elif len(result2) >1:
            avgDist = (float(result2[-1][0]) + float(result2[-1][1]))/2
            if result2[-1][2] == 'mm':
                avgDist = avgDist/10
            return avgDist
    elif len(result1) == 0 and len(result2) == 0:
        return 'no'
    else:
        raise Exception('something went wrong')
    
def ettPositionPhrase(txt):
    #(?:) denotes a non capturing group
    #groups are how you can make logic statements
    
    #This is if you only look for these words 10 non digits after ett
#     phrases =  ['[^\d]{0,10}(?:is|in| )+standard', 'stable', '[^\d]{0,10}(?:is|in| )+appropriate', '[^\d]{0,10}(?:is|in| )+satisfactory position', 
#                 '[^\d]{0,10}(?:is|in| )+unchanged position', 'remains in good position', '[^\d]{0,10}(?:is|in| )+good position', '[^\d]{0,10}(?:is|in| )+unchanged', 
#                 '[^\d]{0,10}(?:is|in| )+adequate position','appropriately positioned']
    #This is if you only want to look at 50 non digits or punctuation after ett 
#     phrases =  ['[^\.?!:;\d]{0,50}(?:is|in| )+standard', 'stable', '[^\.?!:;\d]{0,50}(?:is|in| )+appropriate', '[^\.?!:;\d]{0,50}(?:is|in| )+satisfactory position', 
#                 '[^\.?!:;\d]{0,50}(?:is|in| )+unchanged position', 'remains in good position', '[^\.?!:;\d]{0,50}(?:is|in| )+good position', '[^\.?!:;\d]{0,50}(?:is|in| )+unchanged', 
#                 '[^\.?!:;\d]{0,50}(?:is|in| )+adequate position','appropriately positioned']
    #currently using indefinite non punctuation or digits after ett 
    #!!!added '[^\.?!:;\d]*carina' and all the statements at the end in this list since working on the above. This is because there are lots of example of 
    #"ett at the level of the carina" or 'ett in the right mainstem' and this is still telling me there is a tube present so decided to count it as a position statement

    phrases =  ['[^\.?!:;\d]*(?:is|in| )+standard', 'stable', '[^\.?!:;\d]*(?:is|in| )+appropriate', '[^\.?!:;\d]*(?:is|in| )+satisfactory position', 
                '[^\.?!:;\d]*(?:is|in| )+unchanged position', 'remains in good position', '[^\.?!:;\d]*(?:is|in| )+good position', '[^\.?!:;\d]*(?:is|in| )+unchanged', 
                '[^\.?!:;\d]*(?:is|in| )+adequate position','appropriately positioned', '[^\.?!:;\d]*carina', '[^\.?!:;\d]*mainstem', '[^\.?!:;\d]*main-stem', 
                '[^\.?!:;\d]*should be retracted', '[^\.?!:;\d]*needs to be retracted', '[^\.?!:;\d]*should be pulled back', '[^\.?!:;\d]*high', '[^\.?!:;\d]*should be advanced', 
                '[^\.?!:;\d]*needs to be advanced']    
    
    for phrase in phrases:        
        if re.search(r'##ett## *'+phrase, txt):
            return 1
    return 0

#Probably didn't need a function but wanted the code to look cleaner
#Just uses a for loop to get the attribute from the row (which is passed as a tuple) 
#the list past needs to be a list of integers because I am referencing by index number
def getAttrMulti(row, lst):
    ret = []
    for item in lst:
        ret.append(row[item])
    return ret

#Simple function to that takes the max number in a list of list
#need this function because right now each row reprsents a sentence and not all the text
#So if one sentences has a remove case and all the others have no matched clauses, we could capture everything this way now
#EG rem.in.tr.car.pos
#   [0, 0, 0, 1, 0],  
#   [0, 0, 0, 0, 0], 
#   [0, 0, 0, 1, 1], 
#   [0, 1, 0, 1, 1],
#   [0, 0, 0, 1, 0]]
#Returns
#   [0, 1, 0, 1, 1]
def getMax(lst):
    return pd.DataFrame(lst).max()[1:].to_list() #converts the passed list to a dataframe and then uses the max() function on everyting but the first item in the list("the id") and then returns it as a list

#switch case after getting max list from above statement
#See explanation in comment following this function

def switch(lst):
    lst = tuple(lst) #tuples are immutable and can have duplicates. Also allows for mattching of the whole list and not just a single item in the list
    yesList = [(0,0,0,1,0), (0,0,0,0,1), (0,0,0,1,1), (0,1,0,1,0), (0,1,0,0,0), (0,1,0,0,1), (0,1,0,1,1)]
    noList = [(1,0,0,0,0), (1,0,1,0,0), (0,0,1,0,0)]
    if lst in yesList:
        return 'yes'
    elif lst in noList:
        return 'no'
    else:
        return 'unk'
#Yes List
#Rem-In-Tr-Cari-Pos
# 0	0	0	1	0
# 0	0	0	0	1
# 0	0	0	1	1
# 0	1	0	1	0
# 0	1	0	0	0
# 0	1	0	0	1
# 0	1	0	1	1

#No List
#Rem-In-Tr-Cari-Pos
# 1	0	0	0	0
# 1	0	1	0	0
# 0	0	1	0	0

    
#Function that iterates over every row in the dataframe and comapres the specified rows below
def compareStatements(df):
    ret = {}
    wrkList = [] 
    curRow = []
    rowID = str
    
    
    #change carinaDist(cm) variable to a binary variable for easier processing
    #CANNOT filp the order because if you change 'no' to 0 first, the next statement would change them all to 1
    df = df.copy() #first have to make a copy or it will change the passed dataframe for good and not just within the function
    df.loc[df['carinaDist(cm)'] != 'no', 'carinaDist(cm)'] = 1
    df.loc[df['carinaDist(cm)'] == 'no', 'carinaDist(cm)'] = 0
    
    #MADE ALL THESE FORLOOPS TO COMPSENTATE FOR WHEN I WAS LOOKING AT SENTENCES AND THERE WERE DUPLICATES
    #ISN'T NEEDED WHEN WE ARE JUST LOOKING AT TEXT BUT IT RUNS FINE AND IS RELATIVELY QUICK SO DIDN'T CHANGE IT
    
    #you cannot use special characters in itertuples, so what the itertuples does is instead of using the name as an attribute
    #it will change it to its position in the tuple and represents it as a string '_##' 
    #Or you can reference by the actual integer number tuple [**] (which is what I do later). However, itertuples also adds an additional column called Index, so have to add 1 to the position
    cols = list(df.columns)
    iD = cols.index('id')+1
    ettRem = cols.index('ettRemoved?')+1
    ettIn = cols.index('ettInserted?')+1
    trach = cols.index('trach?')+1
    carinaDist = cols.index('carinaDist(cm)')+1
    ettPos = cols.index('ettPositionStatement')+1
    
    for i, row in enumerate(df.itertuples()): #probably didn't need to enumerate here, but i thought I might want to keep the count later
        
        if not i%1000: print('Processing file {} out of {} ({:.1%})'.format(i+1,len(df),((i+1)/len(df))),end='\r', flush=True)
        #The idea here is we are iterating over each row. Some rows represent the same image, so have to keep track
        #First, just a the attributes of the current row to a list
        #Then go to the next row, if the "IDs" match, add the row to the working list until they don't match
        #Once the IDs don't match, if wrklst contains multiple rows we need to process the list using getMax function
        #Otherwise, if wrklst is just a single row, return that row
        #Basically, we are always processing one row behind what the for loop is on, and because of this, we need a sepearte if statement out side of the foor loop to handle the last row
        
        if not wrkList: #checks if wrkList is empty, which should only be the first case
            rowID = getattr(row, 'id') #keep the id we are trying to match later 
            wrkList.append(getAttrMulti(row, [iD, ettRem, ettIn, trach, carinaDist, ettPos])) #Made getAttrMulti just to make it look cleaner, but unfortunately it is still a for loop
        else: #when wrklist has values (which should always be the case besides the first one) you jump into this else satement
            if rowID == getattr(row, 'id'):
                wrkList.append(getAttrMulti(row, [iD, ettRem, ettIn, trach, carinaDist, ettPos]))
            else:
                if len(wrkList) >1:
                    #see switch function above, but this is the final step to say "yes" ett, "no" or "unk"
                    #returns a dictionary with the ID as the key and the result as a string
                    ret[rowID] = switch(getMax(wrkList))  
                    #now reset worklist and rowID
                    rowID = getattr(row, 'id')
                    wrkList = [getAttrMulti(row, [iD, ettRem, ettIn, trach, carinaDist, ettPos])]
                else:
                    #wrklist is a list of list and for switch funciton to handle just a single list, need to pass it [0][1:] to pass the inner list and then [1:] leaves out the id column
                    #Don't have to do this when the list has multiples because I use getMax function first which returns a single list
                    ret[rowID] = switch(wrkList[0][1:]) #returns a dictionary with the ID as the key and the result as a string
                    rowID = getattr(row, 'id')
                    wrkList = [getAttrMulti(row, [iD, ettRem, ettIn, trach, carinaDist, ettPos])]
        
        if wrkList: #for the last row have to repeat the same if else statement as above
            if len(wrkList) >1:
                    ret[rowID] = switch(getMax(wrkList))
                    #don't need to reset becase it is last row
            else:
                    ret[rowID] = switch(wrkList[0][1:])
    
    print('Processing file {} out of {} ({:.1%})'.format(i+1,len(df),((i+1)/len(df))))    
    return ret


#Opens and reads the DICOM header file
#df = passed dataframe
#pathCol = the column of the dataframe that contains the path directory for each corresponding image study
#idCol = the column of the dataframe that is being used as a unique identifier for each study 
#         (in our code this is patientID_seriesID, eg p10XXXXXX_s########.txt
def getDICOM_data(df, pathCol = 'dicomDir', idCol = 'id'):
    ret = {}
    fileList = []
    idList = []
    pathList = []
    viewList = []
    invertList = []
    seriesList = []
    acqList = []
    instList = []

    errors = {}

    for i, path in enumerate(df[pathCol]):
        if not i%1000: print('Processing dicom file {} of {}: ({:.1%})'.format(i+1, len(df),((i+1)/len(df))),end='\r', flush=True)

        for file in os.listdir(df[pathCol][i]): #step through each image file in the path
            #because every image has a corresponding .html file so don't want to open that 
            if pathlib.Path(file).suffix == '.dcm':
                image_path = os.path.join(df[pathCol][i], file) #make the final path by combinng 
            
                #ds = dicom.dcmread(image_path) will load the entire image
                #dicom.dcmread(image_path, , specific_tags=['PhotometricInterpretation']) will only look for specific tags and not load everything making processing faster
                #There are a few .dcm files that won't load for whatever reason so start with try/except and catch errors
                try:
                    dicom.dcmread(image_path, specific_tags=['ViewPosition'])
                except:
                    errors[file] = df[idCol][i]
                else:
                    ds = dicom.dcmread(image_path, specific_tags=['PhotometricInterpretation', 'ViewPosition', 'SeriesNumber', 'AcquisitionNumber', 'InstanceNumber']) #read to photometric Interpretation

                    fileList.append(file)
                    idList.append(df[idCol][i]) #save the id of the text file
                    pathList.append(df[pathCol][i]) 

                    #Not every dicom header had all of the necessary fields and code would fail if it couldn't find one
                    #This is an EXTREMELY messy way to do things, but I wanted the try, except, else statements all on one line
                    #exec just runs 'text' as code. So if you put \n that prints a new line when it runs 
                    exec("try: ds.ViewPosition\nexcept: viewList.append('')\nelse:viewList.append(ds.ViewPosition)")
                    exec("try: ds.PhotometricInterpretation\nexcept: invertList.append('')\nelse:invertList.append(ds.PhotometricInterpretation)")
                    exec("try: ds.SeriesNumber\nexcept: seriesList.append('')\nelse:seriesList.append(ds.SeriesNumber)")
                    exec("try: ds.AcquisitionNumber\nexcept: acqList.append('')\nelse:acqList.append(ds.AcquisitionNumber)")
                    exec("try: ds.InstanceNumber\nexcept: instList.append('')\nelse:instList.append(ds.InstanceNumber)")
                    #this is how i used to do it
                    #viewList.append(ds.ViewPosition)
                    #invertList.append(ds.PhotometricInterpretation) #save view position AP, PA, LL etc.

    ret = {'file':fileList, pathCol:pathList, idCol:idList, 'view':viewList, 
           'color':invertList, 'series':seriesList, 'acquisition':acqList, 'instance':instList}
    print('Processing dicom file {} of {}: ({:.1%})'.format(i+1, len(df),((i+1)/len(df))))
    return ret, errors

#function to find the lowest series image in an image study that contains multiple images
#df = dataframe passed
##idCol = the column of the dataframe that is being used as a unique identifier for each study 
#         (in our code this is patientID_seriesID, eg p10XXXXXX_s########.txt
#fileCol = column of the dataframe that contains the DICOM file name (should end in .dcm)
#dirCol = column of the dataframe that contains the directory path to the .dcm file
#seriesCol= column of the dataframe that contains the series number of the associated image in the dataframe row (obtained in getDICOM_data function)
#acqCol = column of the dataframe that contains the acquisition number of the associated image in the dataframe row (obtained in getDICOM_data function)
#instCol = column of the dataframe that contains the instance number of the associated image in the dataframe row (obtained in getDICOM_data function)

def getLowestSeries(df, idCol = 'id', fileCol = 'file', dirCol = 'dicomDir', seriesCol = 'series', 
                    acqCol = 'acquisition', instCol = 'instance'):
    ret = {}
    wrkList = [] 
    rowID = str
    
    #returnLists
    idList = []
    fileList = [] 
    seriesList = []
    errID = []
    
    df = df.copy() #first have to make a copy or it will change the passed dataframe for good and not just within the function

        
    #you cannot use special characters in itertuples, so what the itertuples does is instead of using the name as an attribute
    #it will change it to its position in the tuple and represents it as a string '_##' 
    #Or you can reference by the actual integer number tuple [**] (which is what I do later). However, itertuples also adds an additional column called Index, so have to add 1 to the position
    cols = list(df.columns)
    iD = cols.index(idCol)+1
    file = cols.index(fileCol)+1
    directory = cols.index(dirCol)+1
    series = cols.index(seriesCol)+1
    acq = cols.index(acqCol)+1
    instance = cols.index(instCol)+1
    
    for i, row in enumerate(df.itertuples()): #probably didn't need to enumerate here, but i thought I might want to keep the count later
        
        if not i%1000: print('Processing file {} out of {} ({:.1%})'.format(i+1,len(df),((i+1)/len(df))),end='\r', flush=True)
        #The idea here is we are iterating over each row. Some rows represent the same study, so have to keep track
        #First, just a the attributes of the current row to a list
        #Then go to the next row, if the "IDs" match, add the row to the working list until they don't match
        #Once the IDs don't match, if wrklst contains multiple rows we need to process the list using getMin function
        #Otherwise, if wrklst is just a single row, return that row
        #Basically, we are always processing one row behind what the for loop is on, and because of this, we need a sepearte if statement out side of the foor loop to handle the last row
        
        if not wrkList: #checks if wrkList is empty, which should only be the first case
            rowID = getattr(row, idCol) #keep the id we are trying to match later 
            wrkList.append(getAttrMulti(row, [iD, file, directory, series, acq, instance])) #Made getAttrMulti just to make it look cleaner, but unfortunately it is still a for loop
        else: #when wrklist has values (which should always be the case besides the first one) you jump into this else satement
            if rowID == getattr(row, idCol): #if the current row ID is the same as the last row, keep building the working list
                wrkList.append(getAttrMulti(row, [iD, file, directory, series, acq, instance]))
            else: #once the current row id isn't the same, need to decide what to do
                if len(wrkList) >1:
                    tmpList = getMin(wrkList)
                    if len(tmpList)<3:
                        errID.append(tmpList[0])
                    else:
                        idList.append(tmpList[0])
                        fileList.append(tmpList[1])
                        seriesList.append(tmpList[2])
                #now reset worklist and rowID
                rowID = getattr(row, idCol)
                wrkList = [getAttrMulti(row, [iD, file, directory, series, acq, instance])]

        
    if wrkList: #for the last row have to repeat the same if else statement as above
        if len(wrkList) >1:
            tmpList = getMin(wrkList)
            if len(tmpList)<3:
                errID.append(tmpList[0])
            else:
                idList.append(tmpList[0])
                fileList.append(tmpList[1])
                seriesList.append(tmpList[2])
    
    print('Processing file {} out of {} ({:.1%})'.format(i+1,len(df),((i+1)/len(df))),end='\r', flush=True)
    ret = {idCol:idList, fileCol:fileList, seriesCol:seriesList} 
    return ret, errID

def getMin(lst, col = 3):
    ret = []
    #lst = passed list
    #col = the col you want to minimize on
    
    #for this script column 3 is the series
    #make the passed list into a dataframe
    lstDF = pd.DataFrame(lst)
    #0 should be the image id
    #1 should be the image file name
    #if you test for a minimum series value and multiple images have the same series number, return the id and 'error'
    if len(lstDF.loc[lstDF[col] == lstDF[col].min(), [0,1,col]]) >1:
        ret = [lstDF[0][0], 'err']
    #if you test for a minim and only get a single answer, then return the id, imageFileName, and series number
    else:
        ret = lstDF.loc[lstDF[col] == lstDF[col].min(), [0,1,col]].values.flatten().tolist()
    
    return ret