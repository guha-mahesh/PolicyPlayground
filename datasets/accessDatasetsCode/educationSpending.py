import requests
import pandas as pd
import json
import xml.etree.ElementTree as ET
from io import StringIO
import time

def fetch_worldbank_data_json():
    """Fetch data using JSON format"""
    

    url = "https://api.worldbank.org/v2/country/all/indicator/SE.XPD.TOTL.GD.ZS"
    
    params = {
        'format': 'json',
        'per_page': 20000,
        'date': '1999:2024'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        

        if len(data) > 1 and data[1]:
            records = data[1]
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            df['country_name'] = df['country'].apply(lambda x: x['value'] if x else None)
            df['country_code'] = df['country'].apply(lambda x: x['id'] if x else None)
            df['indicator_name'] = df['indicator'].apply(lambda x: x['value'] if x else None)
            df['indicator_code'] = df['indicator'].apply(lambda x: x['id'] if x else None)
            
            # Select and rename columns
            df_clean = df[['country_name', 'country_code', 'indicator_name', 
                          'indicator_code', 'date', 'value']].copy()
            df_clean.columns = ['Country Name', 'Country Code', 'Indicator Name', 
                               'Indicator Code', 'Year', 'Value']
            
            # Convert data types
            df_clean['Year'] = pd.to_numeric(df_clean['Year'], errors='coerce')
            df_clean['Value'] = pd.to_numeric(df_clean['Value'], errors='coerce')
            
            # Remove rows with missing values
            df_clean = df_clean.dropna(subset=['Year', 'Value'])
            
            print(f"Successfully fetched {len(df_clean)} records")
            return df_clean
            
    except requests.exceptions.RequestException as e:
        print(f"couldn't fetch data: {e}")
        return None




if __name__ == "__main__":
    
    df = fetch_worldbank_data_json()


    output_file = "datasets/raw-datasets/education_data.csv"
    df.to_csv(output_file, index=False)
    print(f"\nData saved to: {output_file}")
