import sys
import os
import pandas as pd
import numpy as np
import requests

from backend.policy_api.policy_api import test


def fetch_policies_data():
    try:
        response = test()
        # test() returns a list of tuples from cursor.fetchall()
        data = response.get_json()
        # Convert the list of tuples to a DataFrame
        df = pd.DataFrame(data, columns=[
            'policy_id', 'year_enacted', 'politician', 'topic', 'country',
            'budget', 'duration_length', 'population_size', 'pol_scope',
            'duration', 'intensity', 'advocacy_method', 'pol_description'
        ])
        return df
    except Exception as e:
        print(f"Error in fetch_policies_data: {str(e)}")
        return pd.DataFrame()

def cosineSimilarity(df):
    pass

def predict():
    try:
        policies_df = fetch_policies_data()
        if policies_df.empty:
            return []

        result = policies_df.to_dict(orient='records')
        return result
    except Exception as e:
        print(f"Error in predict: {str(e)}")
        return []


if __name__ == "__main__":
    predict()



