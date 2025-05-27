import requests
import pandas as pd
from bs4 import BeautifulSoup
import io
from urllib.parse import urljoin
import numpy as np

def download_hdi_data(url="https://hdr.undp.org/data-center/documentation-and-downloads"):
    """
    Download HDI Excel file from UNDP website and read it into a pandas DataFrame
    with proper column handling for the multi-level header structure
    
    Args:
        url (str): The UNDP documentation page URL
    
    Returns:
        pandas.DataFrame: The HDI trends data with proper column names
    """
    
    print("Fetching the main page...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    direct_url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Trends_Table.xlsx"
    

    
    try:
        excel_response = requests.get(direct_url, headers=headers)
        excel_response.raise_for_status()
        print("Successfully downloaded the Excel file!")
    except requests.RequestException as e:
        print(f"Error downloading Excel file: {e}")
        return None
    


    excel_content = io.BytesIO(excel_response.content)
    

    excel_file = pd.ExcelFile(excel_content)
    print(f"Excel file contains {len(excel_file.sheet_names)} sheet(s): {excel_file.sheet_names}")
    
    
    target_sheet = excel_file.sheet_names[0]
    
    df_preview = pd.read_excel(excel_content, sheet_name=target_sheet, nrows=10)
    print("Preview of first 10 rows:")
    print(df_preview)
    
    # read the dataset
    df_raw = pd.read_excel(excel_content, sheet_name=target_sheet, header=None)
    
    # Find where the actual data starts by looking for 'HDI rank' and 'Country'
    data_start_row = None
    header_rows = []
    
    # Check first 20 rows for HDI Rank and Country
    for i in range(min(20, len(df_raw))):
        row_str = ' '.join([str(x) for x in df_raw.iloc[i].values if pd.notna(x)])
        if 'HDI rank' in row_str and 'Country' in row_str:
            data_start_row = i
            break
        if any(keyword in row_str for keyword in ['HDI', 'Human Development', 'Value', 'Change']):
            header_rows.append(i)
    
    if data_start_row is None:
        for i in range(min(10, len(df_raw))):
            row = df_raw.iloc[i]
            if pd.notna(row.iloc[0]) and str(row.iloc[0]).isdigit():
                data_start_row = i
                break
    
    print(f"Found data starting at row: {data_start_row}")
    
    if data_start_row is not None:
        column_names = [
            'HDI_rank', 'Country', 
            '1990', '2000', '2010', '2015', '2020', '2021', '2022', '2023',
            'Change_in_HDI_rank_2015_2023',
            'Avg_annual_growth_1990_2000', 'Avg_annual_growth_2000_2010', 
            'Avg_annual_growth_2010_2023', 'Avg_annual_growth_1990_2023'
        ]
        
        df = pd.read_excel(excel_content, sheet_name=target_sheet, 
                            skiprows=data_start_row, header=0)
        
        df = df.dropna(how='all').dropna(axis=1, how='all')
        

        if len(df.columns) >= len(column_names):
            df = df.iloc[:, :len(column_names)]
            df.columns = column_names
        else:
            new_columns = []
            for i, col in enumerate(df.columns):
                if i < len(column_names):
                    new_columns.append(column_names[i])
                else:
                    new_columns.append(f'Column_{i}')
            df.columns = new_columns
        
    else:
        df = df_raw.dropna(how='all').dropna(axis=1, how='all')
        
    df = clean_hdi_dataframe(df)
    
    print(f"Successfully loaded DataFrame with shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    return df
        

def clean_hdi_dataframe(df):
    """
    Clean and format the HDI DataFrame for better usability
    """
    if df is None:
        return None
    
    clean_df = df.copy()
    
    clean_df = clean_df[~clean_df.iloc[:, 1].astype(str).str.contains('Very high human development|High human development|Medium human development|Low human development', na=False)]
    
    if 'HDI_rank' in clean_df.columns:
        clean_df = clean_df[pd.to_numeric(clean_df['HDI_rank'], errors='coerce').notna()]
    else:
        first_col = clean_df.columns[0]
        clean_df = clean_df[pd.to_numeric(clean_df[first_col], errors='coerce').notna()]
    
    numeric_columns = ['1990', '2000', '2010', '2015', '2020', '2021', '2022', '2023']
    for col in numeric_columns:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')
    

    growth_columns = [col for col in clean_df.columns if 'growth' in col.lower() or 'change' in col.lower()]
    for col in growth_columns:
        clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')
    
    clean_df = clean_df.reset_index(drop=True)
    
    return clean_df




if __name__ == "__main__":
    hdi_df = download_hdi_data()
    
    if hdi_df is not None:
        
        # Save to CSV
        output_file = "datasets/raw-datasets/hdi_trends_data.csv"
        hdi_df.to_csv(output_file, index=False)
        print(f"\nData saved to: {output_file}")
        
        
    else:
        print("Failed to download or read the HDI data.")