import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import requests
import json
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)


def fetch_mockaroo_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except:
        return None


def process_uk_data(df):
    if df is None:
        return None, None, None

    if len(df.columns) == 13:
        expected_columns = [
            'month',
            'health_spending_pct_gdp',
            'military_spending_pct_gdp',
            'education_spending_pct_gdp',
            'average BoE BalanceSheet value',
            'average Gilt Holdings',
            'average BankRate values',
            'FTSE Exchange',
            'GBP/USD',
            'GBP/EUR',
            'GBP/JPY',
            'GBP/AUD',
            'GBP/CNY'
        ]
        df.columns = expected_columns

    df['month'] = pd.to_datetime(df['month']).dt.to_period('M')

    uk_spending = df[['month',
                      'health_spending_pct_gdp',
                      'military_spending_pct_gdp',
                      'education_spending_pct_gdp',
                      'average BoE BalanceSheet value',
                      'average Gilt Holdings',
                      'average BankRate values']].copy()

    ftse_data = df[['month', 'FTSE Exchange']].copy()
    ftse_data = ftse_data.rename(columns={'FTSE Exchange': 'close'})

    uk_currencies = {
        "USD": df[['month', 'GBP/USD']].copy().rename(columns={'GBP/USD': 'exchange_value'}),
        "Euro": df[['month', 'GBP/EUR']].copy().rename(columns={'GBP/EUR': 'exchange_value'}),
        "Japanese Yen": df[['month', 'GBP/JPY']].copy().rename(columns={'GBP/JPY': 'exchange_value'}),
        "Australian Dollar": df[['month', 'GBP/AUD']].copy().rename(columns={'GBP/AUD': 'exchange_value'}),
        "Chinese Yuan": df[['month', 'GBP/CNY']].copy().rename(columns={'GBP/CNY': 'exchange_value'})
    }

    return uk_spending, ftse_data, uk_currencies


def process_eu_data(df):
    if df is None:
        return None, None, None

    if len(df.columns) == 13:
        expected_columns = [
            'month',
            'health_spending_pct_gdp',
            'military_spending_pct_gdp',
            'education_spending_pct_gdp',
            'Average ECB Rate Val',
            'Average EU Bond Holdings',
            'average_ECB BalanceSheet value',
            'Stoxx Exchange',
            'EUR/USD',
            'EUR/GBP',
            'EUR/JPY',
            'EUR/AUD',
            'EUR/CNY'
        ]

    if len(df.columns) == len(expected_columns):
        df.columns = expected_columns
    else:
        column_mapping = {}
        for i, col in enumerate(df.columns):
            if i == 0:
                column_mapping[col] = 'month'
            elif 'ECB' in col and 'Rate' in col:
                column_mapping[col] = 'Average ECB Rate Val'
            elif 'Bond' in col or 'Holdings' in col:
                column_mapping[col] = 'Average EU Bond Holdings'
            elif 'Balance' in col or 'BalanceSheet' in col:
                column_mapping[col] = 'average_ECB BalanceSheet value'
            elif 'health' in col.lower():
                column_mapping[col] = 'health_spending_pct_gdp'
            elif 'military' in col.lower():
                column_mapping[col] = 'military_spending_pct_gdp'
            elif 'education' in col.lower():
                column_mapping[col] = 'education_spending_pct_gdp'
            elif 'Stoxx' in col or 'STOXX' in col:
                column_mapping[col] = 'Stoxx Exchange'
            elif 'EUR/USD' in col:
                column_mapping[col] = 'EUR/USD'
            elif 'EUR/GBP' in col:
                column_mapping[col] = 'EUR/GBP'
            elif 'EUR/JPY' in col:
                column_mapping[col] = 'EUR/JPY'
            elif 'EUR/AUD' in col:
                column_mapping[col] = 'EUR/AUD'
            elif 'EUR/CNY' in col:
                column_mapping[col] = 'EUR/CNY'
            else:
                column_mapping[col] = col
        df = df.rename(columns=column_mapping)

    df['month'] = pd.to_datetime(df['month']).dt.to_period('M')

    spending_cols = ['month', 'health_spending_pct_gdp',
                     'military_spending_pct_gdp', 'education_spending_pct_gdp']

    if 'Average ECB Rate Val' in df.columns:
        spending_cols.extend([
            'Average ECB Rate Val',
            'Average EU Bond Holdings',
            'average_ECB BalanceSheet value'
        ])

    eu_spending = df[spending_cols].copy()
    stoxx_data = df[['month', 'Stoxx Exchange']].copy()
    stoxx_data = stoxx_data.rename(columns={'Stoxx Exchange': 'close'})

    eu_currencies = {
        "USD": df[['month', 'EUR/USD']].copy().rename(columns={'EUR/USD': 'exchange_value'}),
        "British Pound": df[['month', 'EUR/GBP']].copy().rename(columns={'EUR/GBP': 'exchange_value'}),
        "Japanese Yen": df[['month', 'EUR/JPY']].copy().rename(columns={'EUR/JPY': 'exchange_value'}),
        "Australian Dollar": df[['month', 'EUR/AUD']].copy().rename(columns={'EUR/AUD': 'exchange_value'}),
        "Chinese Yuan": df[['month', 'EUR/CNY']].copy().rename(columns={'EUR/CNY': 'exchange_value'})
    }

    return eu_spending, stoxx_data, eu_currencies


def normalize_full_df(df):
    df = df.copy()
    for col in df.columns:
        if col == "month":
            continue
        values = df[col]
        if (values >= 0).all() and values.max() > 1000:
            values = np.log1p(values)
        std = values.std()
        if std != 0:
            df[col] = (values - values.mean()) / std
        else:
            df[col] = 0
    return df


def regress(X, y):
    try:
        dot1 = np.dot(X.T, X)
        inv = np.linalg.inv(dot1)
        dot2 = np.dot(X.T, y)
        return np.dot(inv, dot2)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(X.T @ X) @ X.T @ y


def create_currency_model(currency_data, merged_df):
    currency_merged = pd.merge(
        merged_df, currency_data, how="inner", on="month").dropna()
    if len(currency_merged) == 0:
        raise ValueError("No data after merging currency and spending data")
    currency_normalized = normalize_full_df(currency_merged)
    feature_cols = [col for col in currency_normalized.columns
                    if col not in ['close', 'exchange_value', 'month']]
    if len(feature_cols) == 0:
        raise ValueError("No feature columns found")
    X_currency = np.ones((currency_normalized.shape[0], 1))
    X_currency = np.column_stack(
        (X_currency, currency_normalized[feature_cols].values))
    y_currency = np.array(currency_normalized['exchange_value'])
    selected_lags = [1, 2, 3, 6, 9]
    max_lag = max(selected_lags)
    if len(y_currency) <= max_lag:
        selected_lags = [1, 2, 3]
        max_lag = max(selected_lags)
    X_currency = X_currency[max_lag:]
    for lag in selected_lags:
        if max_lag-lag >= 0:
            X_currency = np.column_stack(
                (X_currency, y_currency[max_lag-lag:-lag]))
    y_currency = y_currency[max_lag:]
    return X_currency, y_currency


def train_and_evaluate_model(X, y, model_name):
    try:
        vector = regress(X, y)
        y_pred = np.dot(X, vector)
        residuals = y_pred - y
        r_squared = r2_score(y, y_pred)
        mse = np.mean((y_pred - y) ** 2)
        return vector
    except Exception as e:
        return {
            'model_name': model_name,
            'full_r2': 0.0,
            'full_mse': float('inf'),
            'coefficients': np.array([]),
            'predictions': np.array([]),
            'y_actual': y,
            'residuals': np.array([])
        }


def main():
    uk_api_url = "https://my.api.mockaroo.com/british_data.json?key=5adb7580"
    eu_api_url = "https://my.api.mockaroo.com/europe_data.json?key=5adb7580"

    uk_raw_data = fetch_mockaroo_data(uk_api_url)
    eu_raw_data = fetch_mockaroo_data(eu_api_url)

    uk_success = uk_raw_data is not None
    eu_success = eu_raw_data is not None

    if not uk_success and not eu_success:
        return None

    uk_spending, ftse_data, uk_currencies = None, None, None
    uk_currency_results = {}
    uk_ftse_results = None

    if uk_success:
        uk_spending, ftse_data, uk_currencies = process_uk_data(uk_raw_data)
        if uk_spending is not None:
            uk_merged = pd.merge(uk_spending, ftse_data,
                                 how="inner", on="month")
            uk_normalized = normalize_full_df(uk_merged)
            feature_cols = [
                col for col in uk_normalized.columns if col not in ['close', 'month']]
            X_uk = np.ones((uk_normalized.shape[0], 1))
            X_uk = np.column_stack((X_uk, uk_normalized[feature_cols].values))
            y_uk = np.array(uk_normalized['close'])
            X_uk = X_uk[1:]
            X_uk = np.column_stack((X_uk, y_uk[:-1]))
            y_uk = y_uk[1:]
            uk_ftse_results = train_and_evaluate_model(
                X_uk, y_uk, "UK FTSE 100")
            for name, data in uk_currencies.items():
                try:
                    X_curr, y_curr = create_currency_model(data, uk_merged)
                    results = train_and_evaluate_model(
                        X_curr, y_curr, f"UK {name}")
                    uk_currency_results[name] = results
                except:
                    pass

    eu_spending, stoxx_data, eu_currencies = None, None, None
    eu_currency_results = {}
    eu_stoxx_results = None

    if eu_success:
        eu_spending, stoxx_data, eu_currencies = process_eu_data(eu_raw_data)
        if eu_spending is not None:
            eu_merged = pd.merge(eu_spending, stoxx_data,
                                 how="inner", on="month")
            eu_normalized = normalize_full_df(eu_merged)
            feature_cols = [
                col for col in eu_normalized.columns if col not in ['close', 'month']]
            X_eu = np.ones((eu_normalized.shape[0], 1))
            X_eu = np.column_stack((X_eu, eu_normalized[feature_cols].values))
            y_eu = np.array(eu_normalized['close'])
            X_eu = X_eu[1:]
            X_eu = np.column_stack((X_eu, y_eu[:-1]))
            y_eu = y_eu[1:]
            eu_stoxx_results = train_and_evaluate_model(
                X_eu, y_eu, "EU STOXX 600")
            for name, data in eu_currencies.items():
                try:
                    X_curr, y_curr = create_currency_model(data, eu_merged)
                    results = train_and_evaluate_model(
                        X_curr, y_curr, f"EU {name}")
                    eu_currency_results[name] = results
                except:
                    pass

    return {
        'uk_ftse': uk_ftse_results,
        'uk_currencies': uk_currency_results,
        'eu_stoxx': eu_stoxx_results,
        'eu_currencies': eu_currency_results,
        'uk_data': uk_merged if uk_success else None,
        'eu_data': eu_merged if eu_success else None,
        'uk_raw': uk_raw_data if uk_success else None,
        'eu_raw': eu_raw_data if eu_success else None
    }


if __name__ == "__main__":
    results = main()
    print(results['uk_ftse'])
