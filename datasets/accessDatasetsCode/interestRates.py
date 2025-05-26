import requests
import pandas as pd
import os
from dotenv import load_dotenv

dotenv_path = "/Users/guhamahesh/VSCODE/dialogue/FinFluxes/api/.env"
load_dotenv(dotenv_path)


api_key = os.getenv("FRED_API_KEY")

print(api_key)


def interestRate(type):
    map = {"deposit facility rate": "ECBDFR", "main refinancing operations": "ECBMRRFR",
           "Marginal Lending Facility Rate": "ECBMLFR"}
    code = map[type]
    print
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={api_key}&file_type=json"
    df = pd.read_json(url)
    return df
