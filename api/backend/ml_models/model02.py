import plotly.graph_objects as go
import plotly.express as px
from sklearn.metrics import r2_score
import numpy as np
import requests
import pandas as pd
import os
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd


def monthly_sp500():
    pd.set_option('display.max_columns', None)

    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(start="2003-01-01", end="2024-02-01", interval="1mo")
    df = df.reset_index()

    # Explicitly ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df['month'] = df['Date'].dt.to_period('M')

    df_final = pd.DataFrame({
        'month': df['month'],
        'close': df['Close']
    })

    return df_final


dotenv_path = "/Users/guhamahesh/VSCODE/dialogue/FinFluxes/api/.env"
load_dotenv(dotenv_path)
api_key = os.getenv("FRED_API_KEY")
pd.set_option('display.max_columns', None)


def interestRate(type):
    map = {"federalfundsrate": "FEDFUNDS", "DiscountRate": "INTDSRUSM193N",
           "TreasurySecurities": "WSHOMCB", "FedReserveBalanceSheet": "WALCL"}

    code = map[type.replace(" ", "")]

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    jsondata = response.json()
    df = pd.DataFrame(jsondata["observations"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.rename(columns={'value': f'{type}_value'})

    return df.dropna(subset=[f'{type}_value'])


def exports():

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=NETEXP&api_key={api_key}&file_type=json"
    response = requests.get(url)
    jsondata = response.json()
    df = pd.DataFrame(jsondata["observations"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.rename(columns={'value': f'exports_value'})
    print(url)
    return df.dropna(subset=['exports_value'])


def conversions(currency):

    currency_fred_codes = {
        "Euro (EUR)": "DEXUSEU",         # USD per 1 Euro
        "British Pound (GBP)": "DEXUSUK",  # USD per 1 British Pound
        "Japanese Yen (JPY)": "DEXJPUS",  # JPY per 1 USD (note: inverse)
        "Canadian Dollar (CAD)": "DEXCAUS",  # CAD per 1 USD (inverse)
        "Swiss Franc (CHF)": "DEXSZUS",  # CHF per 1 USD
        "Australian Dollar (AUD)": "DEXUSAL",  # USD per 1 AUD
        "Chinese Yuan (CNY)": "DEXCHUS",  # CNY per 1 USD
        "Indian Rupee (INR)": "DEXINUS",  # INR per 1 USD
        "Mexican Peso (MXN)": "DEXMXUS",  # MXN per 1 USD
        "Brazilian Real (BRL)": "DEXBZUS",  # BRL per 1 USD
        "Russian Ruble (RUB)": "DEXRUS",  # RUB per 1 USD
        "South Korean Won (KRW)": "DEXKOUS",  # KRW per 1 USD
        "Swedish Krona (SEK)": "DEXSDUS",  # SEK per 1 USD
        "Norwegian Krone (NOK)": "DEXNOUS",  # NOK per 1 USD
        "Singapore Dollar (SGD)": "DEXSIUS",  # SGD per 1 USD
        "Hong Kong Dollar (HKD)": "DEXHKUS",  # HKD per 1 USD
        "New Zealand Dollar (NZD)": "DEXUSNZ",  # USD per 1 NZD
        "South African Rand (ZAR)": "DEXSFUS",  # ZAR per 1 USD
        "Turkish Lira (TRY)": "DEXTUUS",  # TRY per 1 USD
        "Israeli Shekel (ILS)": "DEXISUS",  # ILS per 1 USD
    }
    code = currency_fred_codes[currency]
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    jsondata = response.json()
    df = pd.DataFrame(jsondata["observations"])

    # Clean values
    df["exchange_value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["exchange_value"])

    # Convert to Period[M] to remove day
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")

    # Drop duplicate months
    df = df.drop_duplicates(subset="month", keep="first")

    # Filter date range
    df = df[(df["month"] >= "2003-01") & (df["month"] <= "2024-02")]

    return df[["month", "exchange_value"]]


def clean_data(df):
    # Convert 'date' column to pandas Period (year-month only)
    df['date'] = pd.to_datetime(df['date']).dt.to_period('M')
    df = df.iloc[:, 2:4]
    return df


def standardize_dates(dfs):
    new_dfs = []
    # start filtering from 2003-01
    cutoff_date = pd.Period('2003-01', freq='M')
    for df in dfs:
        subset = df[df['date'] >= cutoff_date]  # keep dates >= 2003-01
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
            df[col] = 0  # If constant column, set to 0
    return df


def regress(X, y):
    dot1 = np.dot(X.T, X)
    inv = np.linalg.inv(dot1)
    dot2 = np.dot(X.T, y)
    return np.dot(inv, dot2)


def cross_validate_model(X_data, y_data, model_name):
    """Cross-validation function (one fold - 70/30 split)"""
    n = len(y_data)
    split_point = int(n * 0.7)  # 70% for training

    # Split 1: First 70% train, last 30% test
    X_train1, X_test1 = X_data[:split_point], X_data[split_point:]
    y_train1, y_test1 = y_data[:split_point], y_data[split_point:]

    # Train and predict
    vector1 = regress(X_train1, y_train1)
    y_pred1 = np.dot(X_test1, vector1)

    # Split 2: Last 70% train, first 30% test
    train_size = int(n * 0.7)
    X_train2, X_test2 = X_data[-train_size:], X_data[:-train_size]
    y_train2, y_test2 = y_data[-train_size:], y_data[:-train_size]

    # Train and predict
    vector2 = regress(X_train2, y_train2)
    y_pred2 = np.dot(X_test2, vector2)

    # Calculate metrics for both folds
    r2_fold1 = r2_score(y_test1, y_pred1)
    mse_fold1 = np.mean((y_pred1 - y_test1) ** 2)

    r2_fold2 = r2_score(y_test2, y_pred2)
    mse_fold2 = np.mean((y_pred2 - y_test2) ** 2)

    # Average metrics
    avg_r2 = (r2_fold1 + r2_fold2) / 2
    avg_mse = (mse_fold1 + mse_fold2) / 2

    return avg_r2, avg_mse


def create_currency_model(currency_data, currency_name="Currency"):
    """
    Create a currency model with the same preprocessing as the S&P 500 model.

    Parameters:
    currency_data: DataFrame with currency exchange rate data
    currency_name: String name for the currency (for printing)

    Returns:
    X_currency: Feature matrix with intercept and lag
    y_currency: Target variable (exchange rates)
    """
    # Create currency dataset with proper preprocessing
    currency_merged = pd.merge(
        merged_df, currency_data, how="inner", on="month").dropna()

    # Apply the same transformations as the S&P 500 model
    currency_normalized = normalize_full_df(currency_merged)

    # Create feature matrix with intercept column
    adjusted = currency_normalized.drop(
        columns=['close', 'exchange_value', 'month'])
    X_currency = np.ones((adjusted.shape[0], 1))  # Add intercept column
    X_currency = np.column_stack((X_currency, adjusted.values))
    y_currency = np.array(currency_normalized['exchange_value'])

    # Apply lag transformation
    # Drop first row of X_currency
    X_currency = X_currency[1:]
    # Add lagged y_currency values
    X_currency = np.column_stack((X_currency, y_currency[:-1]))
    # Drop first row of y_currency to match X_currency
    y_currency = y_currency[1:]

    print(f"{currency_name} model data prepared - X shape: {X_currency.shape}, y shape: {y_currency.shape}")

    return X_currency, y_currency


def train_and_evaluate_currency_model(X_currency, y_currency, currency_name="Currency"):
    """
    Train and evaluate a currency model, including cross-validation.

    Parameters:
    X_currency: Feature matrix
    y_currency: Target variable
    currency_name: String name for the currency (for printing)

    Returns:
    Dictionary with model results
    """
    # Train on full dataset
    vector_currency = regress(X_currency, y_currency)
    ypreds_full_currency = np.dot(X_currency, vector_currency)

    # Calculate full dataset metrics
    r_squared_full_currency = r2_score(y_currency, ypreds_full_currency)
    mse_currency = np.mean((ypreds_full_currency - y_currency) ** 2)

    # Cross-validation
    cv_r2, cv_mse = cross_validate_model(
        X_currency, y_currency, f"{currency_name} Model")

    # Store results
    results = {
        'currency_name': currency_name,
        'full_r2': r_squared_full_currency,
        'full_mse': mse_currency,
        'cv_r2': cv_r2,
        'cv_mse': cv_mse,
        'coefficients': vector_currency,
        'predictions': ypreds_full_currency
    }

    return results


# Data loading and processing
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

merged_df = final_dfs[0]

for df in final_dfs[1:]:
    merged_df = pd.merge(merged_df, df, how="inner", on="month")
merged_df = pd.merge(merged_df, sandp, how="inner", on="month")

# Load all currency data
currencies = {
    "Euro": "Euro (EUR)",

    "Japanese Yen": "Japanese Yen (JPY)",
    "Canadian Dollar": "Canadian Dollar (CAD)",
    "Swiss Franc": "Swiss Franc (CHF)",
    "Australian Dollar": "Australian Dollar (AUD)",
    "Chinese Yuan": "Chinese Yuan (CNY)"
}

currency_data = {}
for name, code in currencies.items():
    try:
        data = conversions(code)
        currency_data[name] = data.iloc[:-1]  # Remove last row
        print(f"Loaded {name} data - Shape: {currency_data[name].shape}")
    except Exception as e:
        print(f"Error loading {name}: {e}")

# Filter data BEFORE normalization
# Drop all dates where Treasury Securities data is 0
merged_df = merged_df[merged_df['average_TreasurySecurities_value'] != 0]

# Apply existing filters
merged_df = merged_df[merged_df['average_TreasurySecurities_value'] > -1]

# Apply square root transformation to Fed Reserve Balance Sheet
merged_df['average_FedReserveBalanceSheet_value'] = np.sqrt(
    merged_df['average_FedReserveBalanceSheet_value'])

# Normalize full dataset
data = normalize_full_df(merged_df)

# S&P 500 Model
X = np.ones((data.shape[0], 1))
X = np.column_stack((X, data.drop(columns=['month', 'close']).values))
y = np.array(data['close'])

# Apply lag transformation to S&P 500 model
X = X[1:]                          # Drop first row of X
X = np.column_stack((X, y[:-1]))   # Add lagged y values
y = y[1:]                          # Drop first row of y to match X

# Train S&P 500 model
vector_full = regress(X, y)
ypreds_full = np.dot(X, vector_full)
resids = ypreds_full - y

# Calculate S&P 500 metrics
mse_full = np.mean((ypreds_full - y) ** 2)
r_squared_full = r2_score(y, ypreds_full)
sp500_cv_r2, sp500_cv_mse = cross_validate_model(X, y, "S&P 500")

# Create and evaluate currency models
currency_results = {}
for name, data in currency_data.items():
    try:
        X_currency, y_currency = create_currency_model(data, name)
        results = train_and_evaluate_currency_model(
            X_currency, y_currency, name)
        currency_results[name] = results
    except Exception as e:
        print(f"Error creating model for {name}: {e}")


print(f"\nS&P 500 Model:")
print(f"  Full Dataset - R²: {r_squared_full:.4f}, MSE: {mse_full:.4f}")
print(f"  Cross-Val    - R²: {sp500_cv_r2:.4f}, MSE: {sp500_cv_mse:.4f}")

for name, results in currency_results.items():
    print(f"\n{results['currency_name']} Model:")
    print(
        f"  Full Dataset - R²: {results['full_r2']:.4f}, MSE: {results['full_mse']:.4f}")
    print(
        f"  Cross-Val    - R²: {results['cv_r2']:.4f}, MSE: {results['cv_mse']:.4f}")

# Create summary table
print(f"\n{'Model':<15} {'Full R²':<10} {'Full MSE':<12} {'CV R²':<10} {'CV MSE':<12}")
print("-" * 70)
print(f"{'S&P 500':<15} {r_squared_full:<10.4f} {mse_full:<12.4f} {sp500_cv_r2:<10.4f} {sp500_cv_mse:<12.4f}")

for name, results in currency_results.items():
    print(
        f"{name:<15} {results['full_r2']:<10.4f} {results['full_mse']:<12.4f} {results['cv_r2']:<10.4f} {results['cv_mse']:<12.4f}")


num_cols = [col for col in data.columns if (data[col].dtype == float)]


def plot():
    for col in num_cols:
        lst = data[col].tolist()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=lst,
            y=resids,
            mode='markers',
            name=col,
            marker=dict(size=8, opacity=0.7)
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="red")

        fig.update_layout(
            title=f'Residual Plots versus {col}',
            xaxis_title=col,
            yaxis_title='Residual',
            showlegend=True
        )
        fig.write_html(f'ResidualPlots_{col}.html')
        fig.show()


def plot_feats_no_normal():
    data2 = merged_df.drop(columns=['month', 'close'])

    for col in data2.columns:
        fig = px.scatter(
            x=data2[col],
            y=merged_df['close'],
            color=merged_df['month'].astype(str),
            title=f'The S&P 500 index V.S {col}',
            labels={'x': col, 'y': 'The S&P 500', 'color': 'Month'}
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.write_html(f'The_S&P_500_index_V.S_{col}.html')
        fig.show()


def plot_feats_1():
    data2 = data.drop(columns=['month', 'close'])

    for col in data2.columns:
        fig = px.scatter(
            x=data2[col],
            y=data['close'],
            color=data['month'].astype(str),
            title=f'The S&P 500 index V.S {col}',
            labels={'x': col, 'y': 'The S&P 500', 'color': 'Month'}
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.write_html(f'The_S&P_500_index_V.S_{col}.html')
        fig.show()


weights = {
    'SP500': vector_full,
    **{name: results['coefficients'] for name, results in currency_results.items()}
}

print("Model Weights:")
for model, coeffs in weights.items():
    print(f"{model}: {coeffs}")
