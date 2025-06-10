import numpy as np
import requests
import pandas as pd
import os
from datetime import datetime, timedelta

pd.set_option('display.max_columns', None)


sp500_coefficients_data = None
currency_models = None
merged_df = None
normalization_stats = None


def train():
    """
    Main training function that loads all data from database API and trains models.

    Returns:
        dict: Contains 'sp500_coefficients', 'currency_models', and 'merged_df'
    """
    global sp500_coefficients_data, currency_models, merged_df, normalization_stats

    def fetch_from_api(table_name):
        """Fetch data from database API"""
        url = f"http://web-api:4000/model/fetchData/{table_name}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            df = pd.DataFrame(data, columns=['mos', 'vals'])
            df['vals'] = pd.to_numeric(df['vals'], errors='coerce')
            return df
        else:
            raise Exception(f"Failed to fetch {table_name} from API")

    def load_sp500_data():

        df = fetch_from_api("sp500")
        df['month'] = pd.to_datetime(df['mos']).dt.to_period('M')
        df['close'] = df['vals']
        return df[['month', 'close']]

    def load_fred_data(table_name):
        """Load FRED data from API"""
        df = fetch_from_api(table_name)
        df['date'] = pd.to_datetime(df['mos'])

        value_column_map = {
            "discountrate": "DiscountRate_value",
            "treasurysecurities": "TreasurySecurities_value",
            "FRBS": "FedReserveBalanceSheet_value"
        }
        value_column = value_column_map.get(table_name)
        df[value_column] = df['vals']

        return df[['date', value_column]].dropna()

    def load_currency_data(table_name):
        """Load currency data from API"""
        df = fetch_from_api(table_name)
        df["month"] = pd.to_datetime(df['mos']).dt.to_period("M")
        df['exchange_value'] = df['vals']
        return df[['month', 'exchange_value']]

    def clean_data(df):
        df['date'] = pd.to_datetime(df['date']).dt.to_period('M')
        return df

    def standardize_dates(dfs):
        new_dfs = []
        cutoff_date = pd.Period('2003-01', freq='M')
        for df in dfs:
            subset = df[df['date'] >= cutoff_date]
            new_dfs.append(subset)
        return new_dfs

    def find_averages(df):
        column_name = df.columns[1]
        start_date = pd.Period('2003-01', freq='M')
        end_date = pd.Period('2024-01', freq='M')

        months = []
        averages = []

        current_period = start_date
        while current_period <= end_date:
            month_data = df[df['date'] == current_period]
            avg_value = month_data[column_name].mean(
            ) if not month_data.empty else 0
            months.append(current_period)
            averages.append(avg_value)
            current_period += 1

        result_df = pd.DataFrame({
            'month': months,
            f'average_{column_name}': averages
        })
        return result_df

    def compute_normalization_stats(df):
        stats_dict = {}
        for col in df.columns:
            if col == "month":
                continue
            values = df[col].copy()

            stats_dict[col] = {
                'mean': values.mean(),
                'std': values.std(),
                'log_transformed': False
            }
        return pd.DataFrame(stats_dict).T

    def normalize_full_df(df):
        df = df.copy()
        for col in df.columns:
            if col == "month":
                continue
            values = df[col]

            std = values.std()
            if std != 0:
                df[col] = (values - values.mean()) / std
            else:
                df[col] = 0
        return df

    def regress(X, y):
        dot1 = np.dot(X.T, X)
        inv = np.linalg.inv(dot1)
        dot2 = np.dot(X.T, y)
        return np.dot(inv, dot2)

    def prepare_data():
        fred_tables = ["discountrate", "treasurysecurities", "FRBS"]
        dfs_to_concat = []

        for table in fred_tables:
            dfs_to_concat.append(load_fred_data(table))

        dfs = [clean_data(df) for df in dfs_to_concat]
        new_dfs = standardize_dates(dfs)

        final_dfs = []
        for df in new_dfs:
            final_dfs.append(find_averages(df))

        sandp = load_sp500_data()

        merged_df = final_dfs[0]
        for df in final_dfs[1:]:
            merged_df = pd.merge(merged_df, df, how="inner", on="month")
        merged_df = pd.merge(merged_df, sandp, how="inner", on="month")

        merged_df = merged_df[merged_df['average_TreasurySecurities_value'] != 0]
        merged_df = merged_df[merged_df['average_TreasurySecurities_value'] > -1]

        return merged_df

    def train_sp500_model(merged_df):

        global normalization_stats
        normalization_stats = compute_normalization_stats(merged_df)

        data = normalize_full_df(merged_df)

        X = np.ones((data.shape[0], 1))
        X = np.column_stack((X, data.drop(columns=['month', 'close']).values))
        y = np.array(data['close'])

        selected_lags = [1, 2, 3, 6, 9]
        max_lag = max(selected_lags)

        X = X[max_lag:]

        for lag in selected_lags:
            X = np.column_stack((X, y[max_lag-lag:-lag]))

        y = y[max_lag:]

        coefficients = regress(X, y)
        return coefficients, data

    def train_currency_model(merged_df, currency_data, currency_name):
        currency_merged = pd.merge(
            merged_df, currency_data[['month', 'exchange_value']],
            how="inner", on="month"
        ).dropna()

        currency_stats = compute_normalization_stats(
            currency_merged[['exchange_value']]
        )
        normalization_stats.loc[f'{currency_name}_exchange_value'] = currency_stats.loc['exchange_value']

        currency_normalized = normalize_full_df(currency_merged)

        adjusted = currency_normalized.drop(
            columns=['close', 'exchange_value', 'month'])
        X_currency = np.ones((adjusted.shape[0], 1))
        X_currency = np.column_stack((X_currency, adjusted.values))
        y_currency = np.array(currency_normalized['exchange_value'])

        selected_lags = [1, 2, 3, 6, 9]
        max_lag = max(selected_lags)
        X_currency = X_currency[max_lag:]

        for lag in selected_lags:
            X_currency = np.column_stack(
                (X_currency, y_currency[max_lag-lag:-lag]))

        y_currency = y_currency[max_lag:]

        coefficients = regress(X_currency, y_currency)
        return coefficients

    merged_df = prepare_data()

    sp500_coefficients, normalized_data = train_sp500_model(merged_df)
    sp500_coefficients_data = sp500_coefficients

    currency_tables = {
        "Euro": "EUROTOUSD",
        "Japanese Yen": "JPYtoUSD",
        "Australian Dollar": "AUDtoUSD",
        "Chinese Yuan": "YuantoUSD",
        "British Pound": "GBPtoUSD"
    }

    currency_models = {}
    for name, table in currency_tables.items():
        try:
            currency_data = load_currency_data(table).iloc[:-1]
            coefficients = train_currency_model(merged_df, currency_data, name)
            currency_models[name] = coefficients
        except Exception as e:
            print(f"Error training {name} model: {e}")

    api_base_url = "http://web-api:4000/model"

    sp500_payload = {
        "model_name": "sp500",
        "coefficients": sp500_coefficients_data.tolist()
    }

    response = requests.post(
        f"{api_base_url}/storeWeights", json=sp500_payload)
    if response.status_code != 200:
        print(f"Failed to store S&P 500 weights: {response.text}")

    for currency_name, coefficients in currency_models.items():
        currency_payload = {
            "model_name": f"currency_{currency_name}",
            "coefficients": coefficients.tolist()
        }

        response = requests.post(
            f"{api_base_url}/storeWeights", json=currency_payload)
        if response.status_code != 200:
            print(f"Failed to store {currency_name} weights: {response.text}")

    return {
        "status": "success",
        "models_trained": ["sp500"] + [f"currency_{name}" for name in currency_models.keys()]
    }


def predict_sp500(user_features, coefficients=None):
    """
    Predict S&P 500 closing price with proper normalization
    """
    global normalization_stats

    if normalization_stats is None:
        raise ValueError("Model must be trained before making predictions")

    if coefficients is None:
        response = requests.get("http://web-api:4000/model/getWeights/sp500")
        if response.status_code == 200:
            coefficients = np.array(response.json()['coefficients'])
        else:
            raise ValueError("Failed to fetch S&P 500 model weights from API")

    url = "http://web-api:4000/model/fetchData/sp500"
    response = requests.get(url)
    data = response.json()['data']
    sp500_df = pd.DataFrame(data, columns=['mos', 'vals'])
    sp500_df['Date'] = pd.to_datetime(sp500_df['mos'])
    sp500_df['close'] = pd.to_numeric(sp500_df['vals'])
    sp500_df = sp500_df.sort_values('Date')

    current_date = datetime.now()
    months_back = [1, 2, 3, 6, 9]
    lag_values = []

    for months in months_back:
        target_date = current_date - timedelta(days=months*30)
        available_data = sp500_df[sp500_df['Date'] <= target_date]

        if not available_data.empty:
            closing_price = available_data.iloc[-1]['close']
            lag_values.append(closing_price)
        else:
            lag_values.append(4000)

    X = np.ones([1])

    discount_rate = user_features[0]
    discount_norm = (discount_rate - normalization_stats.loc['average_DiscountRate_value', 'mean']) / \
        normalization_stats.loc['average_DiscountRate_value', 'std']
    X = np.column_stack((X, discount_norm))

    treasury_value = user_features[1]

    treasury_norm = (treasury_value - normalization_stats.loc['average_TreasurySecurities_value', 'mean']) / \
        normalization_stats.loc['average_TreasurySecurities_value', 'std']
    X = np.column_stack((X, treasury_norm))

    fed_value = user_features[2]

    fed_norm = (fed_value - normalization_stats.loc['average_FedReserveBalanceSheet_value', 'mean']) / \
        normalization_stats.loc['average_FedReserveBalanceSheet_value', 'std']
    X = np.column_stack((X, fed_norm))

    close_mean = normalization_stats.loc['close', 'mean']
    close_std = normalization_stats.loc['close', 'std']

    for lag_value in lag_values:

        lag_normalized = (lag_value - close_mean) / (close_std)
        X = np.column_stack((X, lag_normalized))

    prediction_normalized = np.dot(X, coefficients)[0]

    prediction_denorm = (prediction_normalized * close_std) + close_mean

    prediction_real = prediction_denorm

    return prediction_real


def predict_currency(user_features, currency_models_dict=None):
    """
    Predict currency exchange rates

    Args:
        user_features: [discount_rate, treasury_securities, fed_balance_sheet]
        currency_models_dict: Dictionary of trained currency models (fetches from API if not provided)

    Returns:
        dict: Predicted exchange rates for all currencies
    """
    global normalization_stats

    if normalization_stats is None:
        raise ValueError("Model must be trained before making predictions")

    if currency_models_dict is None:
        currency_models_dict = {}
        currencies = ["Euro", "Japanese Yen",
                      "Australian Dollar", "Chinese Yuan", "British Pound"]

        for currency in currencies:
            response = requests.get(
                f"http://web-api:4000/model/getWeights/currency_{currency}")
            if response.status_code == 200:
                currency_models_dict[currency] = np.array(
                    response.json()['coefficients'])
            else:
                print(f"Warning: Could not fetch weights for {currency}")

    currency_table_map = {
        "Euro": "EUROTOUSD",
        "Japanese Yen": "JPYtoUSD",
        "Australian Dollar": "AUDtoUSD",
        "Chinese Yuan": "YuantoUSD",
        "British Pound": "GBPtoUSD"
    }

    predictions = {}

    for currency_name, table_name in currency_table_map.items():
        if currency_name not in currency_models_dict:
            continue

        currency_coefficients = currency_models_dict[currency_name]

        url = f"http://web-api:4000/model/fetchData/{table_name}"
        response = requests.get(url)
        data = response.json()['data']
        historical_currency_data = pd.DataFrame(data, columns=['mos', 'vals'])
        historical_currency_data["month"] = pd.to_datetime(
            historical_currency_data["mos"]).dt.to_period("M")
        historical_currency_data['exchange_value'] = pd.to_numeric(
            historical_currency_data['vals'])

        current_date = datetime.now()
        months_back = [1, 2, 3, 6, 9]
        lag_values = []

        for months in months_back:
            target_date = current_date - timedelta(days=months*30)
            target_period = pd.Period(target_date.strftime('%Y-%m'), freq='M')

            available_data = historical_currency_data[historical_currency_data['month'] <= target_period]

            if not available_data.empty:
                closest_rate = available_data['exchange_value'].iloc[-1]
                lag_values.append(closest_rate)
            else:
                lag_values.append(1.0)

        X = np.ones([1])

        discount_rate = user_features[0]
        discount_norm = (discount_rate - normalization_stats.loc['average_DiscountRate_value', 'mean']) / \
            normalization_stats.loc['average_DiscountRate_value', 'std']
        X = np.column_stack((X, discount_norm))

        treasury_value = user_features[1]

        treasury_norm = (treasury_value - normalization_stats.loc['average_TreasurySecurities_value', 'mean']) / \
            normalization_stats.loc['average_TreasurySecurities_value', 'std']
        X = np.column_stack((X, treasury_norm))

        fed_value = user_features[2]

        fed_norm = (fed_value - normalization_stats.loc['average_FedReserveBalanceSheet_value', 'mean']) / \
            normalization_stats.loc['average_FedReserveBalanceSheet_value', 'std']
        X = np.column_stack((X, fed_norm))

        currency_stats_key = f'{currency_name}_exchange_value'
        currency_mean = normalization_stats.loc[currency_stats_key, 'mean']
        currency_std = normalization_stats.loc[currency_stats_key, 'std']

        for lag_value in lag_values:

            lag_normalized = (lag_value - currency_mean) / currency_std
            X = np.column_stack((X, lag_normalized))

        prediction_normalized = np.dot(X, currency_coefficients)[0]

        prediction_denorm = (prediction_normalized *
                             currency_std) + currency_mean

        prediction_real = prediction_denorm

        predictions[currency_name] = prediction_real

    return predictions
