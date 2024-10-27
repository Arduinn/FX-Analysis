import pandas as pd
import os
import glob
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# import csv

currencies_folder = "../data/raw/"

# Dictionary to hold DataFrames
dataframes = {}

# Iterate through all files in the folder
for filename in os.listdir(currencies_folder):
    if filename.endswith('.csv'):
        # Construct full file path
        file_path = os.path.join(currencies_folder, filename)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Use the filename (without .csv) as the key for the DataFrame
        key = os.path.splitext(filename)[0]  # Remove the .csv extension
        dataframes[key] = df
        
def pcaCoinModeling(df_currencies, csv_name):
    
    # Replace missing values with the value from the cell below
    df_currencies.fillna(df_currencies, inplace=True)
    
    # Drop rows with missing values
    df_currencies.dropna(inplace=True)
    
    # Store Date Column
    data_index = df_currencies["Date"]
    
    # Drop the 'Date' column
    df_currencies.drop(columns=['Date'], inplace=True)
    
    # Set the target currency
    target_currency = df_currencies.columns[0]

    
    # Standardize the currency data (excluding the target currency)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_currencies.drop(columns=[target_currency]))

    # Perform PCA with 2 components
    pca = PCA(n_components=2)
    pca_components = pca.fit_transform(scaled_data)
    
    # Create a DataFrame for the principal components
    pca_df = pd.DataFrame(data=pca_components, columns=['PC1', 'PC2'])
    
    # Create a DataFrame for the principal components
    pca_df = pd.DataFrame(data=pca_components, columns=['PC1', 'PC2'])

    # Combine PCA components with the target currency
    target_values = df_currencies[target_currency].reset_index(drop=True)
    combined_data = pd.concat([pca_df, target_values], axis=1)
    
    combined_data.index = data_index
     
    csvExport_path = "../data/processed/"
    
    combined_data.to_csv(f"{csvExport_path}/{csv_name}_PCA.csv", index=True, sep=";") 
    
    return None

csvExport_path = "../data/processed/"

# Create a pattern to match all CSV files
csv_pattern = os.path.join(csvExport_path, '*.csv')

# Use glob to find all CSV files
csv_files = glob.glob(csv_pattern)

# Loop through the list of CSV files and delete each one
for csv_file in csv_files:
    try:
        os.remove(csv_file)  # Delete the file
        print(f"Deleted: {csv_file}")
    except Exception as e:
        print(f"Error deleting {csv_file}: {e}")

for coinBasket in dataframes.keys():
    # print(pd.DataFrame(dataframes[coinBasket]))
    pcaCoinModeling(dataframes[coinBasket], coinBasket)
