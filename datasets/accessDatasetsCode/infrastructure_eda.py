import requests
import pandas as pd

def fetch_worldbank_data(indicator, countries, start_year, end_year):
    url = (
        f"https://api.worldbank.org/v2/country/{';'.join(countries)}/indicator/{indicator}"
        f"?format=json&date={start_year}:{end_year}&per_page=500"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")
    data = response.json()
    if len(data) < 2:
        return pd.DataFrame()
    df = pd.json_normalize(data[1])
    df = df[['country.value', 'date', 'value']]
    df.columns = ['Country', 'Year', 'Value']
    return df

countries = ['USA', 'DEU', 'FRA']
indicator = 'SE.XPD.TOTL.GD.ZS'
start_year = 2010
end_year = 2023

df = fetch_worldbank_data(indicator, countries, start_year, end_year)
print(df.head())
