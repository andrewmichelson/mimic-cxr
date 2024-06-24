print('Importing libraries and functions...')
from imports import * #import libraries from seperate imports.py file (needs to be in same directory as current)
from utilities import * #import functions from seperate utilities.py file (needs to be in same directory as current)

# Define input folder and filenames
replacedWordsFile = 'reportText_replacedWords.csv'
pathDirectoryOutputFile = 'paths.csv'
csvSaveDirectory = os.path.join(os.getcwd(), 'CSV Files')

# Define output folder and filenames
nlpPredictionsFile = 'nlpPredictions.csv'

# Load the replaced words file created in openFiles_and_replaceText.py
print('Opening ' + replacedWordsFile + ' file...')
df_ett = pd.read_csv(os.path.join(csvSaveDirectory, replacedWordsFile))

# Process text: replace dimensions, remove extra spaces, and drop duplicates
df_ett['text'] = df_ett['text'].apply(lambda x: replaceDimensions(x)) # Replace millimeter and centimeter in the text
df_ett['text'] = df_ett['text'].apply(lambda x: re.sub(r' {2,}', r' ', x)) # Remove extra spaces
#if report contained multiple instances of the word ETT (like ett and endotracheal tube) then we will have duplicate rows with same info. Keep last because then all of the words will have been changed based on how the output of openFiles_and_replaceText.py functions
df_ett.drop_duplicates(subset='file', keep='last', inplace=True) 
df_ett.reset_index(drop=True, inplace=True) # Reset index after dropping duplicates

# Extract radiology report impressions
df_ett['impression'] = df_ett['text'].apply(getImpression)

# Create a unique identifier based on the file path
df_ett['id'] = df_ett['file'].apply(getPathID)

# Reorder columns to make 'id' the second column
cols = list(df_ett.columns)
newOrder = [cols[0], 'id'] + cols[1:-1]
df_ett = df_ett[newOrder]

# Look for specific statements in the text and add corresponding columns
df_ett['ettRemoved?'] = df_ett['text'].apply(isRemoved) # Flag removal statements
df_ett['ettInserted?'] = df_ett['text'].apply(isInserted) # Flag insertion statements
df_ett['trach?'] = df_ett['text'].apply(isTrach) # Flag tracheostomy presence
df_ett['carinaDist(cm)'] = df_ett['text'].apply(getCarinaDistance) # Get carina distance
df_ett['ettPositionStatement'] = df_ett['text'].apply(ettPositionPhrase) # Determine if position statement is present

# Process predictions for all text
print('Processing predictions for all text.')
allTextDF = pd.DataFrame.from_dict(compareStatements(df_ett), orient='index')

# Format allTextDF for readability
allTextDF.reset_index(level=None, drop=False, inplace=True)
allTextDF.rename(columns={0: 'ett', 'index': 'id'}, inplace=True)

# Process predictions based on impression text
print('\nProcessing predictions based on impression text')
unkIDs = allTextDF.loc[allTextDF['ett'] == 'unk', 'id'].to_list() # List of unknown IDs
df_imp = df_ett.loc[df_ett['id'].isin(unkIDs)].copy() # Filter df_ett to only include unknown IDs
df_imp.drop(df_imp.loc[df_imp['impression'] == 'no impression'].index, inplace=True) # Drop rows without impressions

# Drop specific columns as they will be recalculated based on impressions
df_imp.drop(['ettRemoved?', 'ettInserted?', 'trach?', 'carinaDist(cm)', 'ettPositionStatement'], axis=1, inplace=True)

# Recalculate flags based on impression text
df_imp['ettRemoved?'] = df_imp['impression'].apply(isRemoved)
df_imp['ettInserted?'] = df_imp['impression'].apply(isInserted)
df_imp['trach?'] = df_imp['impression'].apply(isTrach)
df_imp['carinaDist(cm)'] = df_imp['impression'].apply(getCarinaDistance)
df_imp['ettPositionStatement'] = df_imp['impression'].apply(ettPositionPhrase)

# Run compareStatements function on impression text
impressionDF = pd.DataFrame.from_dict(compareStatements(df_imp), orient='index')

# Format impressionDF for readability
impressionDF.reset_index(level=None, drop=False, inplace=True)
impressionDF.rename(columns={0: 'ett', 'index': 'id'}, inplace=True)

# Update allTextDF with new 'yes' statements based on impression text
newYs = impressionDF.loc[impressionDF['ett'] == 'yes', 'id'].tolist()
print("Number of new yes statements based on impression text: ", len(newYs))
allTextDF.loc[allTextDF['id'].isin(newYs), 'ett'] = 'yes'

# Merge final predictions with file paths
finalPredictionsDF = pd.merge(df_ett[['file', 'id', 'carinaDist(cm)']], allTextDF, how='outer', on='id')
finalPredictionsDF['dir'] = finalPredictionsDF['file'].apply(lambda x: os.path.splitext(x)[0]) # Remove file extension
finalPredictionsDF.drop(['file', 'dir'], axis=1, inplace=True) # Drop unnecessary columns
finalPredictionsDF = finalPredictionsDF[['id', 'ett', 'carinaDist(cm)']] # Reorder columns

# Import paths.csv to get all text reports in the database
df_paths = pd.read_csv(os.path.join(csvSaveDirectory, pathDirectoryOutputFile))
df_paths['id'] = df_paths['merged_path'].apply(getPathID)
df_paths['dir'] = df_paths['merged_path'].apply(lambda x: os.path.splitext(x)[0])
df_paths.drop(['i0', 'i1', 'i2', 'file_name', 'merged_path'], axis=1, inplace=True) # Drop unnecessary columns

# Merge predictions with all file paths
mergedDF = pd.merge(df_paths, finalPredictionsDF, on='id', how='outer')

#convert all Nans to No
mergedDF.loc[mergedDF['ett'].isna(), 'ett'] = 'no'

# Save final NLP predictions
print('Saving final NLP predictions to: ' + str(os.path.join(csvSaveDirectory, nlpPredictionsFile)))
mergedDF.to_csv(os.path.join(csvSaveDirectory, nlpPredictionsFile), index=False)

