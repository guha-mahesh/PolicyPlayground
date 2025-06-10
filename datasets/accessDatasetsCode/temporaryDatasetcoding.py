import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from sklearn.metrics import r2_score
import numpy as np
import requests
import pandas as pd
import os
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


def monthly_sp500():
    """Fetch S&P 500 data with CSV caching"""
    csv_file = "data/sp500_monthly.csv"

    # Try to read from CSV first
    if os.path.exists(csv_file):
        print(f"Reading S&P 500 data from {csv_file}")
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df['month'] = pd.to_datetime(df['month']).dt.to_period('M')
        return df[['month', 'close']]

    # If CSV doesn't exist, fetch from API
    print("Fetching S&P 500 data from Yahoo Finance...")
    pd.set_option('display.max_columns', None)

    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(start="2003-01-01", end="2024-02-01", interval="1mo")
    df = df.reset_index()

    # Explicitly ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df['month'] = df['Date'].dt.to_period('M')

    df_final = pd.DataFrame({
        'Date': df['Date'],
        'month': df['month'],
        'close': df['Close']
    })

    # Save to CSV
    os.makedirs("data", exist_ok=True)
    df_final.to_csv(csv_file, index=False)
    print(f"Saved S&P 500 data to {csv_file}")

    return df_final[['month', 'close']]


dotenv_path = "/Users/guhamahesh/VSCODE/dialogue/FinFluxes/api/.env"
load_dotenv(dotenv_path)
api_key = os.getenv("FRED_API_KEY")
pd.set_option('display.max_columns', None)


def interestRate(type):
    """Fetch interest rate data with CSV caching"""
    csv_file = f"data/{type.replace(' ', '_')}_data.csv"

    # Try to read from CSV first
    if os.path.exists(csv_file):
        print(f"Reading {type} data from {csv_file}")
        df = pd.read_csv(csv_file)
        return df.dropna(subset=[f'{type}_value'])

    # If CSV doesn't exist, fetch from API
    print(f"Fetching {type} data from FRED API...")
    map = {"federalfundsrate": "FEDFUNDS", "DiscountRate": "INTDSRUSM193N",
           "TreasurySecurities": "WSHOMCB", "FedReserveBalanceSheet": "WALCL"}

    code = map[type.replace(" ", "")]

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    jsondata = response.json()
    df = pd.DataFrame(jsondata["observations"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.rename(columns={'value': f'{type}_value'})

    # Save to CSV
    os.makedirs("data", exist_ok=True)
    df.to_csv(csv_file, index=False)
    print(f"Saved {type} data to {csv_file}")

    return df.dropna(subset=[f'{type}_value'])


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
    """Original normalization function WITH log transforms"""
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


def normalize_full_df_no_log(df):
    """Modified normalization function WITHOUT log transforms"""
    df = df.copy()
    for col in df.columns:
        if col == "month":
            continue

        values = df[col]

        # NO LOG TRANSFORM - just standardize
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


# Main execution
if __name__ == "__main__":
    # Configuration flag - CHANGE THIS TO SWITCH BETWEEN METHODS
    USE_LOG_TRANSFORM = True  # Set to True for log transform, False for no log transform

    if USE_LOG_TRANSFORM:
        print("Starting S&P 500 analysis WITH log transforms...")
    else:
        print("Starting S&P 500 analysis WITHOUT log transforms...")
    print("=" * 70)

    # fred code map
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

    # Filter data BEFORE normalization
    # Drop all dates where Treasury Securities data is 0
    merged_df = merged_df[merged_df['average_TreasurySecurities_value'] != 0]
    # Apply existing filters
    merged_df = merged_df[merged_df['average_TreasurySecurities_value'] > -1]

    print("\nData shape before normalization:", merged_df.shape)
    print("\nColumn statistics BEFORE normalization (NO LOG TRANSFORMS):")
    print("-" * 70)

    for col in merged_df.columns:
        if col != "month":
            values = merged_df[col]
            print(f"{col}:")
            print(f"  Mean: {values.mean():.4f}")
            print(f"  Std:  {values.std():.4f}")
            print(f"  Min:  {values.min():.4f}")
            print(f"  Max:  {values.max():.4f}")
            print()

    # Choose which normalization to use
    USE_LOG_TRANSFORM = True  # Set to True to use log transform, False to disable

    if USE_LOG_TRANSFORM:
        print("\nUsing normalization WITH log transforms...")
        data = normalize_full_df(merged_df)
    else:
        print("\nUsing normalization WITHOUT log transforms...")
        data = normalize_full_df_no_log(merged_df)

    # S&P 500 Model
    X = np.ones((data.shape[0], 1))
    X = np.column_stack((X, data.drop(columns=['month', 'close']).values))
    y = np.array(data['close'])

    # Apply lag transformation to S&P 500 model
    X = X[1:]
    X = np.column_stack((X, y[:-1]))
    y = y[1:]

    # Train S&P 500 model on full dataset
    vector_full = regress(X, y)
    ypreds_full = np.dot(X, vector_full)
    resids = ypreds_full - y

    # Calculate S&P 500 metrics
    mse_full = np.mean((ypreds_full - y) ** 2)
    r_squared_full = r2_score(y, ypreds_full)

    # Perform cross-validation
    sp500_cv_r2, sp500_cv_mse = cross_validate_model(X, y, "S&P 500")

    # Print results
    print("\n" + "=" * 70)
    if USE_LOG_TRANSFORM:
        print("S&P 500 MODEL RESULTS (WITH LOG TRANSFORMS)")
    else:
        print("S&P 500 MODEL RESULTS (WITHOUT LOG TRANSFORMS)")
    print("=" * 70)
    print(f"\nFull Dataset Performance:")
    print(f"  R-squared: {r_squared_full:.4f}")
    print(f"  MSE:       {mse_full:.4f}")
    print(f"\nCross-Validation Performance (70/30 split, 2 folds):")
    print(f"  Average R-squared: {sp500_cv_r2:.4f}")
    print(f"  Average MSE:       {sp500_cv_mse:.4f}")

    # Print model coefficients
    print(f"\nModel Coefficients:")
    print(f"  Intercept: {vector_full[0]:.4f}")
    print(f"  Discount Rate: {vector_full[1]:.4f}")
    print(f"  Treasury Securities: {vector_full[2]:.4f}")
    print(f"  Fed Reserve Balance Sheet: {vector_full[3]:.4f}")
    print(f"  Lagged S&P 500: {vector_full[4]:.4f}")

    # Create a simple diagnostic plot
    plt.figure(figsize=(12, 8))

    # Subplot 1: Actual vs Predicted
    plt.subplot(2, 2, 1)
    plt.scatter(y, ypreds_full, alpha=0.6)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
    plt.xlabel('Actual S&P 500 (normalized)')
    plt.ylabel('Predicted S&P 500 (normalized)')
    plt.title('Actual vs Predicted Values')
    plt.grid(True, alpha=0.3)

    # Subplot 2: Residuals vs Fitted
    plt.subplot(2, 2, 2)
    plt.scatter(ypreds_full, resids, alpha=0.6)
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.8)
    plt.xlabel('Fitted Values')
    plt.ylabel('Residuals')
    plt.title('Residuals vs Fitted Values')
    plt.grid(True, alpha=0.3)

    # Subplot 3: Histogram of Residuals
    plt.subplot(2, 2, 3)
    plt.hist(resids, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('Residuals')
    plt.ylabel('Frequency')
    plt.title('Distribution of Residuals')
    plt.grid(True, alpha=0.3)

    # Subplot 4: QQ Plot
    plt.subplot(2, 2, 4)
    from scipy import stats
    stats.probplot(resids, dist="norm", plot=plt)
    plt.title('QQ Plot of Residuals')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.suptitle('S&P 500 Model Diagnostics (No Log Transforms)',
                 y=1.02, fontsize=14)
    plt.savefig('sp500_diagnostics_no_log.png', dpi=300, bbox_inches='tight')
    plt.show()

    print("\n" + "=" * 70)
    print("Analysis complete! Diagnostic plot saved as 'sp500_diagnostics_no_log.png'")
