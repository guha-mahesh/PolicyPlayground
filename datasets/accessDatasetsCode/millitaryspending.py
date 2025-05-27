import requests
import zipfile
import io
import pandas as pd

url = "https://api.worldbank.org/v2/en/indicator/MS.MIL.XPND.GD.ZS?downloadformat=csv"

response = requests.get(url)
files_data = {}


def millitaryPercentage():
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        for file_name in zip_file.namelist():
            if file_name.endswith('.csv'):

                with zip_file.open(file_name) as csv_file:
                    # Read the entire content as text first
                    content = csv_file.read().decode('utf-8')

                    # Split into lines and find where the actual data starts
                    lines = content.split('\n')

                    # Look for the header row (usually contains "Country Name", "Country Code", etc.)
                    data_start = 0
                    for i, line in enumerate(lines):
                        if 'Country Name' in line or 'country' in line.lower():
                            data_start = i
                            break

                    # Create a new CSV content starting from the data
                    if data_start > 0:
                        clean_content = '\n'.join(lines[data_start:])
                        df = pd.read_csv(io.StringIO(clean_content))
                    else:
                        # If no clear header found, try the original approach
                        df = pd.read_csv(io.StringIO(content))

                    files_data[file_name] = df

    df_military = files_data['API_MS.MIL.XPND.GD.ZS_DS2_en_csv_v2_337778.csv']
    return df_military


print(millitaryPercentage())
