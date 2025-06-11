import sys
import os
import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity

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
            'duration', 'intensity', 'advocacy_method', 'pol_description',
        ])
        return df
    except Exception as e:
        print(f"Error in fetch_policies_data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error


def preprocess_features(df):
    """
    Preprocess features: normalize numeric features to 0-1 and one hot encode categorical features
    """
    processed_df = df.copy()
    

    numeric_features = ['budget', 'duration_length', 'population_size', 'year_enacted']
    categorical_features = ['topic', 'country']
    
    # Handle missing values for numeric features
    for feature in numeric_features:
        processed_df[feature] = pd.to_numeric(processed_df[feature], errors='coerce')
        processed_df[feature].fillna(processed_df[feature].median(), inplace=True)
    
    # Normalize numeric features to 0-1 range
    for feature in numeric_features:
        if feature == 'year_enacted':
            # encode years from 0 to 1
            processed_df[feature] = (processed_df[feature] - 2000) / (2020 - 2000)
        else:
            # Min max normalization for other numeric features
            min_val = processed_df[feature].min()
            max_val = processed_df[feature].max()
            if max_val != min_val:
                processed_df[feature] = (processed_df[feature] - min_val) / (max_val - min_val)
            else:
                processed_df[feature] = 0.5  # If all values are same, set to middle
    

    categorical_encoded = pd.get_dummies(processed_df[categorical_features], prefix=categorical_features)
    

    feature_matrix = pd.concat([
        processed_df[numeric_features],
        categorical_encoded
    ], axis=1)
    
    return feature_matrix


def cosineSimilarity(target_features, all_features):
    """
    Calculate cosine similarity between target policy and all policies
    """

    if target_features.ndim == 1:
        target_features = target_features.reshape(1, -1)
    

    similarities = cosine_similarity(target_features, all_features)
    return similarities[0]


def predict(index_policy):
    try:
        policies_df = fetch_policies_data()
        if policies_df.empty:
            return []
        

        if index_policy not in policies_df['policy_id'].values:
            return []
        

        target_idx = policies_df[policies_df['policy_id'] == index_policy].index[0]
        

        feature_matrix = preprocess_features(policies_df)
        

        target_features = feature_matrix.iloc[target_idx].values
        

        similarities = cosineSimilarity(target_features, feature_matrix.values)
        

        similarity_scores = list(enumerate(similarities))
        
        # Sort by similarity score in descending order
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top 5 most similar policies (excluding the target policy itself)
        top_similar = []
        for idx, score in similarity_scores:
            if idx != target_idx:
                top_similar.append((idx, score))
            if len(top_similar) == 5:
                break
        

        similar_policies = []
        for idx, score in top_similar:
            policy_data = policies_df.iloc[idx].to_dict()
            policy_data['similarity_score'] = float(score)
            similar_policies.append(policy_data)
        
        return similar_policies
    
    except Exception as e:
        print(f"Error in predict: {str(e)}")
        return []


if __name__ == "__main__":
    result = predict(1)  # Example with policy_id 1
    print(f"Found {len(result)} similar policies")
    for i, policy in enumerate(result, 1):
        print(f"{i}. Policy ID: {policy['policy_id']}, "
              f"Topic: {policy['topic']}, "
              f"Country: {policy['country']}, "
              f"Similarity: {policy['similarity_score']:.4f}")