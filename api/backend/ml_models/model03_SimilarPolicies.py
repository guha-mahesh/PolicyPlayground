import sys
import os
import pandas as pd
import numpy as np
import requests

from backend.policy_api.policy_api import test


def fetch_policies_data():
    response = test()
    data = response.json()
    # Convert the data to a DataFrame with specific columns
    df = pd.DataFrame(data, columns=[
        'policy_id', 'year_enacted', 'politician', 'topic', 'country',
        'budget', 'duration_length', 'population_size'
    ])
    return df

def cosineSimilarity(df):
    pass

def predict():
    policies_df = fetch_policies_data()
    # Print the first few rows to verify the data
    print(policies_df.head())
    return policies_df


if __name__ == "__main__":
    predict()



