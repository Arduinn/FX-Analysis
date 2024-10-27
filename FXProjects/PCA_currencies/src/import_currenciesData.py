import yaml
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import os
import glob

# Importing Data

class CurrencyBasket:
    def __init__(self, yaml_file):
        # Load YAML data and retrieve first-level keys
        with open(yaml_file, 'r') as file:
            self.currencies_data = yaml.safe_load(file)
        self.first_level_keys = list(self.currencies_data.keys())
    
    def download_yfData(self, currencies_list):
        # Create an empty DataFrame to store currency data
        currency_data_df = pd.DataFrame()
        
        # Define date range for data fetching
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=15 * 365)).strftime('%Y-%m-%d')

        # Loop through each currency in the currencies_list and download historical data
        for curr in currencies_list:
            print(f"Downloading data for {curr}...")  # Debug output
            try:
                # Fetch historical data
                data = yf.download(curr, start=start_date, end=end_date)
                date_column = data.index
                if not data.empty:
                    currency_data_df[curr] = data['Close']
                else:
                    print(f"No data found for {curr}")
            except Exception as e:
                print(f"An error occurred while downloading data for {curr}: {e}")
                

        
        currency_data_df.columns = currency_data_df.columns.str.replace('=X', '', regex=False)
        
        return currency_data_df  # Return the DataFrame containing historical currency data

    def display_options(self):
        # Display the list of top-level keys (currencies)
        print("Choose which currency you would like to process:\n", self.first_level_keys)

    def get_currency_data(self, currency):
        # Retrieve data for a specific currency if it exists
        return self.currencies_data.get(currency, "Currency not found.")

    def prompt_and_process(self):
        csvExport_path = "../data/raw/"
        
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
                
        # Display available options
        self.display_options()
        
        # Prompt the user for input and store the choice
        currency = input("Enter the currency you would like to process: ").strip().upper()
        
        # Process the choice and perform specific actions based on the currency
        if currency == "BRL":
            print("You selected Brazilian Real (BRL).")
            # Add specific processing for BRL here
            emerg_basket = self.currencies_data[currency].get('emergents', [])
            comm_basket = self.currencies_data[currency].get('commodities', [])

            # Download data
            brl_emerg = self.download_yfData(emerg_basket)  # Store the returned DataFrame
            brl_comm = self.download_yfData(comm_basket)    # Store the returned DataFrame
            
            # Save CSV
            brl_emerg.to_csv(f"{csvExport_path}/{currency}_emerg.csv", index=True)
            brl_comm.to_csv(f"{csvExport_path}/{currency}_comm.csv", index=True) 
            
            

            print("Downloaded BRL data") 
        
        elif currency == "MXN":
            print("You selected Mexican Peso (MXN).")
            # Add specific processing for BRL here
            emerg_basket = self.currencies_data[currency].get('emergents', [])

            # Download data
            mxn_emerg = self.download_yfData(emerg_basket)  # Store the returned DataFrame
            
            # Save CSV
            mxn_emerg.to_csv(f"{csvExport_path}/{currency}_emerg.csv", index=True)
            
        elif currency == "COP":
            print("You selected Colobian Peso (COP).")
            # Add specific processing for BRL here
            emerg_basket = self.currencies_data[currency].get('emergents', [])
            comm_basket = self.currencies_data[currency].get('commodities', [])

            # Download data
            cop_emerg = self.download_yfData(emerg_basket)  # Store the returned DataFrame
            cop_comm = self.download_yfData(comm_basket)    # Store the returned DataFrame
            
            # Save CSV
            cop_emerg.to_csv(f"{csvExport_path}/{currency}_emerg.csv", index=True)
            cop_comm.to_csv(f"{csvExport_path}/{currency}_comm.csv", index=True) 
            
            
        else:
            # Handle cases where the currency is not BRL or MXN
            print("You selected:", currency)
            currency_data = self.get_currency_data(currency)
            print(f"Data for {currency}:", currency_data)

            # Define date range for data fetching
            end_date = datetime.today().strftime('%Y-%m-%d')
            start_date = (datetime.today() - timedelta(days=15 * 365)).strftime('%Y-%m-%d')

        return "Code Completed"

# Usage
currency_basket = CurrencyBasket("currenciesBasket.yaml")

# Prompt user and process the selected currency
historical_data = currency_basket.prompt_and_process()
