import numpy as np
import requests
import pandas as pd
import os
from dotenv import load_dotenv
import yfinance as yf
from datetime import datetime, timedelta

pd.set_option('display.max_columns', None)


def monthly_sp500():
    """Fetch S&P 500 data with CSV caching"""
    csv_file = "data/sp500_monthly.csv"

    if os.path.exists(csv_file):

        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df['month'] = pd.to_datetime(df['month']).dt.to_period('M')
        return df[['month', 'close']]

    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(start="2003-01-01", end="2024-02-01", interval="1mo")
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    df['month'] = df['Date'].dt.to_period('M')

    df_final = pd.DataFrame({
        'Date': df['Date'],
        'month': df['month'],
        'close': df['Close']
    })

    os.makedirs("data", exist_ok=True)
    df_final.to_csv(csv_file, index=False)

    return df_final[['month', 'close']]


# Load environment variables
dotenv_path = "/Users/guhamahesh/VSCODE/dialogue/FinFluxes/api/.env"
load_dotenv(dotenv_path)
api_key = os.getenv("FRED_API_KEY")


def interestRate(type):
    """Fetch interest rate data with CSV caching"""
    csv_file = f"data/{type.replace(' ', '_')}_data.csv"

    if os.path.exists(csv_file):

        df = pd.read_csv(csv_file)
        return df.dropna(subset=[f'{type}_value'])

    map = {"federalfundsrate": "FEDFUNDS", "DiscountRate": "INTDSRUSM193N",
           "TreasurySecurities": "WSHOMCB", "FedReserveBalanceSheet": "WALCL"}

    code = map[type.replace(" ", "")]
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    jsondata = response.json()
    df = pd.DataFrame(jsondata["observations"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.rename(columns={'value': f'{type}_value'})

    os.makedirs("data", exist_ok=True)
    df.to_csv(csv_file, index=False)

    return df.dropna(subset=[f'{type}_value'])


def conversions(currency):
    """Fetch currency conversion data with CSV caching"""
    safe_currency_name = currency.replace(
        " ", "_").replace("(", "").replace(")", "")
    csv_file = f"data/currency_{safe_currency_name}_data.csv"

    if os.path.exists(csv_file):

        df = pd.read_csv(csv_file)
        df["month"] = pd.to_datetime(df["month"]).dt.to_period("M")
        return df[["month", "exchange_value"]]

    currency_fred_codes = {
        "Euro (EUR)": "DEXUSEU",
        "British Pound (GBP)": "DEXUSUK",
        "Japanese Yen (JPY)": "DEXJPUS",
        "Canadian Dollar (CAD)": "DEXCAUS",
        "Swiss Franc (CHF)": "DEXSZUS",
        "Australian Dollar (AUD)": "DEXUSAL",
        "Chinese Yuan (CNY)": "DEXCHUS",
        "Indian Rupee (INR)": "DEXINUS",
        "Mexican Peso (MXN)": "DEXMXUS",
        "Brazilian Real (BRL)": "DEXBZUS",
        "Russian Ruble (RUB)": "DEXRUS",
        "South Korean Won (KRW)": "DEXKOUS",
        "Swedish Krona (SEK)": "DEXSDUS",
        "Norwegian Krone (NOK)": "DEXNOUS",
        "Singapore Dollar (SGD)": "DEXSIUS",
        "Hong Kong Dollar (HKD)": "DEXHKUS",
        "New Zealand Dollar (NZD)": "DEXUSNZ",
        "South African Rand (ZAR)": "DEXSFUS",
        "Turkish Lira (TRY)": "DEXTUUS",

    }

    code = currency_fred_codes[currency]
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    jsondata = response.json()
    df = pd.DataFrame(jsondata["observations"])

    df["exchange_value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["exchange_value"])
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
    df = df.drop_duplicates(subset="month", keep="first")
    df = df[(df["month"] >= "2003-01") & (df["month"] <= "2024-02")]

    result_df = df[["month", "exchange_value"]]

    os.makedirs("data", exist_ok=True)
    result_df_to_save = result_df.copy()
    result_df_to_save["month"] = result_df_to_save["month"].astype(str)
    result_df_to_save.to_csv(csv_file, index=False)

    return result_df


def clean_data(df):
    df['date'] = pd.to_datetime(df['date']).dt.to_period('M')
    df = df.iloc[:, 2:4]
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
    dot1 = np.dot(X.T, X)
    inv = np.linalg.inv(dot1)
    dot2 = np.dot(X.T, y)
    return np.dot(inv, dot2)


def prepare_data():

    # FRED code map
    map = {
        "DiscountRate": "INTDSRUSM193N",
        "TreasurySecurities": "WSHOMCB",
        "FedReserveBalanceSheet": "WALCL"
    }

    dfs_to_concat = []
    for key in map.keys():
        dfs_to_concat.append(interestRate(key))

    dfs = [clean_data(df) for df in dfs_to_concat]
    new_dfs = standardize_dates(dfs)

    final_dfs = []
    for df in new_dfs:
        final_dfs.append(find_averages(df))

    sandp = monthly_sp500()

    # Merge all data
    merged_df = final_dfs[0]
    for df in final_dfs[1:]:
        merged_df = pd.merge(merged_df, df, how="inner", on="month")
    merged_df = pd.merge(merged_df, sandp, how="inner", on="month")

    # Apply filters
    merged_df = merged_df[merged_df['average_TreasurySecurities_value'] != 0]
    merged_df = merged_df[merged_df['average_TreasurySecurities_value'] > -1]

    return merged_df


def train_sp500_model(merged_df):
    """Train S&P 500 prediction model with multiple lags"""
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


def train_currency_model(merged_df, currency_data):
    """Train currency prediction model"""
    currency_merged = pd.merge(
        merged_df, currency_data, how="inner", on="month").dropna()
    currency_normalized = normalize_full_df(currency_merged)

    # Create feature matrix
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


sp500_coefficients_data = None
currencies = None

merged_df = prepare_data()


sp500_coefficients, normalized_data = train_sp500_model(merged_df)
sp500_coefficients_data = sp500_coefficients

currencies = {
    "Euro": "Euro (EUR)",
    "Japanese Yen": "Japanese Yen (JPY)",
    "Australian Dollar": "Australian Dollar (AUD)",
    "Chinese Yuan": "Chinese Yuan (CNY)",
    "British Pound": "British Pound (GBP)"
}

currency_models = {}
for name, code in currencies.items():
    try:
        currency_data = conversions(code).iloc[:-1]
        coefficients = train_currency_model(merged_df, currency_data)
        currency_models[name] = coefficients

    except Exception as e:
        print(f"Error training {name} model: {e}")
currencies = currency_models


def predict_sp500(user_features, coefficients=sp500_coefficients_data):
    """
    API prediction function

    Args:
        user_features: [discount_rate, treasury_securities, fed_balance_sheet] - user inputs
        coefficients: Pre-trained model coefficients

    Returns:
        float: Predicted S&P 500 closing price
    """

    current_date = datetime.now()
    months_back = [1, 2, 3, 6, 9]
    target_dates = []
    for months in months_back:
        days_back = months * 30
        target_date = current_date - timedelta(days=days_back)
        target_dates.append(target_date)

    earliest_date = min(target_dates) - timedelta(days=10)

    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(start=earliest_date.strftime("%Y-%m-%d"),
                       end=current_date.strftime("%Y-%m-%d"))

    lag_values = []
    for i, target_date in enumerate(target_dates):
        months = months_back[i]
        available_data = df[df.index.date <= target_date.date()]

        if not available_data.empty:
            closest_date = available_data.index[-1]
            closing_price = available_data.loc[closest_date, 'Close']
            lag_values.append(closing_price)
        else:
            lag_values.append(4000)

    X = np.ones([1])

    for feature in user_features:
        X = np.column_stack((X, feature))

    for lag_value in lag_values:
        X = np.column_stack((X, lag_value))

    for i in range(1, 4):
        if X[0, i] >= 0 and X[0, i] > 1000:
            X[0, i] = np.log1p(X[0, i])

    transformed_df = merged_df.copy()
    for col in ['average_TreasurySecurities_value']:
        if (transformed_df[col] >= 0).all() and transformed_df[col].max() > 1000:
            transformed_df[col] = np.log1p(transformed_df[col])
    # Normalize each feature using training stats
    X[0, 1] = (X[0, 1] - transformed_df['average_DiscountRate_value'].mean()
               ) / transformed_df['average_DiscountRate_value'].std()
    X[0, 2] = (X[0, 2] - transformed_df['average_TreasurySecurities_value'].mean()
               ) / transformed_df['average_TreasurySecurities_value'].std()
    X[0, 3] = (X[0, 3] - transformed_df['average_FedReserveBalanceSheet_value'].mean()
               ) / transformed_df['average_FedReserveBalanceSheet_value'].std()

    # Normalize lag values
    sp500_mean = transformed_df['close'].mean()
    sp500_std = transformed_df['close'].std()
    for i in range(4, 9):
        X[0, i] = (X[0, i] - sp500_mean) / sp500_std

    prediction_normalized = np.dot(X, coefficients)[0]
    prediction_real = (prediction_normalized * sp500_std) + sp500_mean

    return prediction_real


def predict_currency(user_features, currency_models=currencies):
    """
    API prediction function for all currencies

    Args:
        user_features: [discount_rate, treasury_securities, fed_balance_sheet] - user inputs
        currency_models: Dictionary of trained currency model coefficients

    Returns:
        dict: Predicted currency exchange rates for all currencies
    """

    currencies_map = {
        "Euro": "Euro (EUR)",
        "Japanese Yen": "Japanese Yen (JPY)",
        "Australian Dollar": "Australian Dollar (AUD)",
        "Chinese Yuan": "Chinese Yuan (CNY)",
        "British Pound": "British Pound (GBP)"
    }

    predictions = {}

    for currency_name, currency_code in currencies_map.items():
        if currency_name not in currency_models:
            continue

        currency_coefficients = currency_models[currency_name]

        current_date = datetime.now()
        months_back = [1, 2, 3, 6, 9]
        target_dates = []
        for months in months_back:
            days_back = months * 30
            target_date = current_date - timedelta(days=days_back)
            target_dates.append(target_date)

        historical_currency_data = conversions(currency_code)

        lag_values = []
        for i, target_date in enumerate(target_dates):
            months = months_back[i]
            target_period = pd.Period(target_date.strftime('%Y-%m'), freq='M')

            available_data = historical_currency_data[historical_currency_data['month'] <= target_period]

            if not available_data.empty:
                closest_rate = available_data['exchange_value'].iloc[-1]
                lag_values.append(closest_rate)
            else:

                lag_values.append(1.0)

        X = np.ones([1])

        for feature in user_features:
            X = np.column_stack((X, feature))

        for lag_value in lag_values:
            X = np.column_stack((X, lag_value))

        # Apply same transformations as in prepare_data() and train_currency_model()
        for i in range(1, 4):
            if X[0, i] >= 0 and X[0, i] > 1000:
                X[0, i] = np.log1p(X[0, i])

        # Now normalize the entire feature vector (same as normalize_full_df does)
        # Get the stats from your transformed training data
        transformed_df = merged_df.copy()
        for col in ['average_TreasurySecurities_value']:
            if (transformed_df[col] >= 0).all() and transformed_df[col].max() > 1000:
                transformed_df[col] = np.log1p(transformed_df[col])

        # Normalize each feature using training stats
        X[0, 1] = (X[0, 1] - transformed_df['average_DiscountRate_value'].mean()
                   ) / transformed_df['average_DiscountRate_value'].std()
        X[0, 2] = (X[0, 2] - transformed_df['average_TreasurySecurities_value'].mean()
                   ) / transformed_df['average_TreasurySecurities_value'].std()
        X[0, 3] = (X[0, 3] - transformed_df['average_FedReserveBalanceSheet_value'].mean()
                   ) / transformed_df['average_FedReserveBalanceSheet_value'].std()

        # Normalize lag values using currency stats
        currency_mean = historical_currency_data['exchange_value'].mean()
        currency_std = historical_currency_data['exchange_value'].std()
        for i in range(4, 9):
            X[0, i] = (X[0, i] - currency_mean) / currency_std

        prediction_normalized = np.dot(X, currency_coefficients)[0]
        prediction_real = (prediction_normalized *
                           currency_std) + currency_mean

        predictions[currency_name] = prediction_real

    return predictions
