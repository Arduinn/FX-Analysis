import pandas as pd
import os
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import glob

# Import Data

pca_data = "../data/processed/"

# Dictionary to hold DataFrames
seriesData = {}

# Iterate through all files in the folder
for filename in os.listdir(pca_data):
    if filename.endswith('.csv'):
        # Construct full file path
        file_path = os.path.join(pca_data, filename)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path, sep=";")
        
        # Use the filename (without .csv) as the key for the DataFrame
        key = os.path.splitext(filename)[0]  # Remove the .csv extension
        seriesData[key] = df
        
# Processing Data

# Dictionary to hold DataFrames
resultData = {}

size_train = 0.94

for pca_basket in seriesData.keys():
    
    pca_data = seriesData[pca_basket]
    
    # Select Currency Column
    target_currency = pca_data.columns[3]
    
    row_add = 0
    
    final_dataset = pd.DataFrame(columns=[target_currency, pca_basket ])
    
    while row_add < pca_data.shape[0] - 730:  # Ensure enough data for a full slice
        
        # Slice Data with a 2-year (730 days) window
        slice_df = pca_data.iloc[row_add : (2 * 365) + row_add]
        
        # Check if slice_df has enough data for training
        if len(slice_df) < 730:
            break
        
        # Split the data into training and testing sets
        train_size = int(len(slice_df) * size_train)
        train_data = slice_df[:train_size]
        test_data = slice_df[train_size:]
        
        try:
            # Fit the ARIMA model on the training data
            model = ARIMA(train_data[target_currency], exog=train_data[['PC1', 'PC2']], order=(0, 0, 0))
            model_fit = model.fit()
            
            # Forecast future values using the test data
            forecast = model_fit.forecast(steps=len(test_data), exog=test_data[['PC1', 'PC2']])

            # Add the forecast results to the test DataFrame
            test_data[pca_basket] = forecast
            
            # Select the actual and forecasted values and assign dates
            result_df = test_data[[target_currency, pca_basket]]
            
            # Ensure the index of result_df is set correctly based on the dates from slice_df
            result_df.index = slice_df["Date"].iloc[train_size:].reset_index(drop=True)

            # Concatenate along rows, giving priority to slice_df on overlapping indices
            final_dataset = pd.concat([final_dataset[~final_dataset.index.isin(result_df.index)], result_df], axis=0)
            
            # Reset the index to ensure consistency after each iteration
            final_dataset = final_dataset.sort_index()

            # Update row_add to shift the slice window by 7 days
            row_add += 7

        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally, break the loop on errors to avoid an infinite loop
            break

    # Store the results for the current pca_basket
    resultData[pca_basket] = final_dataset  # Store final_dataset instead of result_df

# Specify the export path
export_path = "../data/projection/"

# Create the export directory if it does not exist
os.makedirs(export_path, exist_ok=True)

# Create a pattern to match all CSV files
csv_pattern = os.path.join(export_path, '*.csv')

# Use glob to find all CSV files
csv_files = glob.glob(csv_pattern)

# Loop through the list of CSV files and delete each one
for csv_file in csv_files:
    try:
        os.remove(csv_file)  # Delete the file
        print(f"Deleted: {csv_file}")
    except Exception as e:
        print(f"Error deleting {csv_file}: {e}")

# Loop through each DataFrame in the resultData dictionary and save it to CSV
for name in resultData.keys():
    # Construct the full file path
    file_path = os.path.join(export_path, f"{name}.csv")
    # Save the DataFrame to CSV
    resultData[name].to_csv(file_path, sep=";", index=True)  # Set index=True if you want to include the index