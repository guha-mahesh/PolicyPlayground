import sys
import os
import pandas as pd
import numpy as np
import requests

from backend.policy_api.policy_api import test


def fetch_policies_data():
    response = test()
    data = response.json()
    df = pd.DataFrame(data)
    return df

def cosineSimilarity(df):
    pass

def predict():
    policies_df = fetch_policies_data()
    policies_df.print()


if __name__ == "__main__":
    predict()



