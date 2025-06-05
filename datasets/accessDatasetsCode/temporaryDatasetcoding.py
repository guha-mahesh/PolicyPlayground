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


def exports():
    """Fetch exports data with CSV caching"""
    csv_file = "data/exports_data.csv"

    # Try to read from CSV first
    if os.path.exists(csv_file):
        print(f"Reading exports data from {csv_file}")
        df = pd.read_csv(csv_file)
        return df.dropna(subset=['exports_value'])

    # If CSV doesn't exist, fetch from API
    print("Fetching exports data from FRED API...")
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=NETEXP&api_key={api_key}&file_type=json"
    response = requests.get(url)
    jsondata = response.json()
    df = pd.DataFrame(jsondata["observations"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.rename(columns={'value': f'exports_value'})

    # Save to CSV
    os.makedirs("data", exist_ok=True)
    df.to_csv(csv_file, index=False)
    print(f"Saved exports data to {csv_file}")
    print(url)

    return df.dropna(subset=['exports_value'])


def conversions(currency):
    """Fetch currency conversion data with CSV caching"""
    safe_currency_name = currency.replace(
        " ", "_").replace("(", "").replace(")", "")
    csv_file = f"data/currency_{safe_currency_name}_data.csv"

    # Try to read from CSV first
    if os.path.exists(csv_file):
        print(f"Reading {currency} data from {csv_file}")
        df = pd.read_csv(csv_file)
        df["month"] = pd.to_datetime(df["month"]).dt.to_period("M")
        return df[["month", "exchange_value"]]

    # If CSV doesn't exist, fetch from API
    print(f"Fetching {currency} data from FRED API...")
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

    result_df = df[["month", "exchange_value"]]

    # Save to CSV
    os.makedirs("data", exist_ok=True)
    # Convert month to string for CSV storage
    result_df_to_save = result_df.copy()
    result_df_to_save["month"] = result_df_to_save["month"].astype(str)
    result_df_to_save.to_csv(csv_file, index=False)
    print(f"Saved {currency} data to {csv_file}")

    return result_df


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
    X_currency: Feature matrix with intercept and specific lags
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

    # Specify exactly which lags you want (e.g., 1, 2, 3, 6, 9 months)
    selected_lags = [1, 2, 3, 6, 9]
    max_lag = max(selected_lags)  # Use the maximum lag as the starting point

    # Start with base features (drop first max_lag months)
    X_currency = X_currency[max_lag:]

    # Add each selected lag
    for lag in selected_lags:
        X_currency = np.column_stack(
            (X_currency, y_currency[max_lag-lag:-lag]))

    # Adjust y to match
    y_currency = y_currency[max_lag:]

    return X_currency, y_currency


def train_and_evaluate_currency_model(X_currency, y_currency, currency_name="Currency"):
    """
    Train and evaluate a currency model, including cross-validation.
    """
    # Train on full dataset
    vector_currency = regress(X_currency, y_currency)
    ypreds_full_currency = np.dot(X_currency, vector_currency)

    # Calculate residuals
    resids_currency = ypreds_full_currency - y_currency

    # Calculate full dataset metrics
    r_squared_full_currency = r2_score(y_currency, ypreds_full_currency)
    mse_currency = np.mean((ypreds_full_currency - y_currency) ** 2)

    # Cross-validation
    cv_r2, cv_mse = cross_validate_model(
        X_currency, y_currency, f"{currency_name} Model")

    # Store results including actual y values
    results = {
        'currency_name': currency_name,
        'full_r2': r_squared_full_currency,
        'full_mse': mse_currency,
        'cv_r2': cv_r2,
        'cv_mse': cv_mse,
        'coefficients': vector_currency,
        'predictions': ypreds_full_currency,
        'y_actual': y_currency,  # Store actual values
        'residuals': resids_currency  # Store residuals
    }

    return results


# INTERACTIVE PLOTTING FUNCTIONS
def interactive_plot_feats(data):
    """Interactive version of plot_feats"""
    data['month_str'] = data['month'].astype(str)

    features = ['average_DiscountRate_value',
                'average_TreasurySecurities_value',
                'average_FedReserveBalanceSheet_value']

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=[feat.replace("average_", "").replace(
            "_value", "") + " Over Time" for feat in features],
        vertical_spacing=0.08
    )

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    for i, feat in enumerate(features):
        clean_name = feat.replace("average_", "").replace("_value", "")

        fig.add_trace(
            go.Scatter(
                x=data["month_str"],
                y=data[feat],
                name=clean_name,
                line=dict(color=colors[i], width=2.5),
                hovertemplate=f'<b>{clean_name}</b><br>Date: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
            ),
            row=i+1, col=1
        )

    fig.update_layout(
        title='Financial Features Over Time (Interactive)',
        height=800,
        showlegend=False,
        hovermode='x unified'
    )

    fig.update_xaxes(tickangle=45)
    fig.show()
    fig.write_html("features_over_time.html")


def interactive_plot_features_vs_sp500(data):
    """Interactive version of plot_features_vs_sp500"""

    features = [
        'average_DiscountRate_value',
        'average_TreasurySecurities_value',
        'average_FedReserveBalanceSheet_value'
    ]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[feat.replace('average_', '').replace(
            '_value', '') + ' vs S&P 500' for feat in features],
        horizontal_spacing=0.08
    )

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    for i, feature in enumerate(features):
        clean_name = feature.replace('average_', '').replace('_value', '')

        # Add scatter plot
        fig.add_trace(
            go.Scatter(
                x=data[feature],
                y=data['close'],
                mode='markers',
                name=clean_name,
                marker=dict(
                    color=colors[i],
                    size=8,
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                hovertemplate=f'<b>{clean_name}</b>: %{{x:.2f}}<br><b>S&P 500</b>: %{{y:.2f}}<extra></extra>'
            ),
            row=1, col=i+1
        )

        # Add trendline
        z = np.polyfit(data[feature], data['close'], 1)
        p = np.poly1d(z)
        correlation = data[feature].corr(data['close'])

        fig.add_trace(
            go.Scatter(
                x=data[feature],
                y=p(data[feature]),
                mode='lines',
                name=f'{clean_name} Trend',
                line=dict(color='red', width=2, dash='dash'),
                showlegend=False,
                hovertemplate=f'Trendline (Corr: {correlation:.3f})<extra></extra>'
            ),
            row=1, col=i+1
        )

    fig.update_layout(
        title='Features vs S&P 500 (Interactive)',
        height=500,
        showlegend=False
    )

    fig.show()
    fig.write_html("features_vs_sp500.html")


def interactive_sp500_diagnostic_plots(residuals, predictions, title="S&P 500 Model"):
    """Interactive version of create_sp500_diagnostic_plots"""

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Residuals vs Fitted Values (Linearity & Homoscedasticity)',
            'Residuals vs Time Index (Autocorrelation Check)',
            'Scale-Location Plot (Homoscedasticity)',
            'Histogram of Residuals'
        ],
        horizontal_spacing=0.08,
        vertical_spacing=0.1
    )

    # 1. Residuals vs Fitted
    fig.add_trace(
        go.Scatter(
            x=predictions,
            y=residuals,
            mode='markers',
            name='Residuals vs Fitted',
            marker=dict(color='blue', size=6, opacity=0.6),
            hovertemplate='Fitted: %{x:.3f}<br>Residual: %{y:.3f}<extra></extra>'
        ),
        row=1, col=1
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)

    # 2. Residuals vs Index
    fig.add_trace(
        go.Scatter(
            x=list(range(len(residuals))),
            y=residuals,
            mode='markers',
            name='Residuals vs Index',
            marker=dict(color='green', size=6, opacity=0.6),
            hovertemplate='Index: %{x}<br>Residual: %{y:.3f}<extra></extra>'
        ),
        row=1, col=2
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=2)

    # 3. Scale-Location Plot
    sqrt_abs_resid = np.sqrt(np.abs(residuals))
    fig.add_trace(
        go.Scatter(
            x=predictions,
            y=sqrt_abs_resid,
            mode='markers',
            name='Scale-Location',
            marker=dict(color='orange', size=6, opacity=0.6),
            hovertemplate='Fitted: %{x:.3f}<br>√|Residual|: %{y:.3f}<extra></extra>'
        ),
        row=2, col=1
    )

    # 4. Histogram of Residuals
    fig.add_trace(
        go.Histogram(
            x=residuals,
            name='Residuals Distribution',
            marker_color='purple',
            opacity=0.7,
            hovertemplate='Residual: %{x:.3f}<br>Count: %{y}<extra></extra>'
        ),
        row=2, col=2
    )

    fig.update_layout(
        title=f'{title} - Interactive Diagnostic Plots',
        height=800,
        showlegend=False
    )

    # Update axis labels
    fig.update_xaxes(title_text="Fitted Values", row=1, col=1)
    fig.update_yaxes(title_text="Residuals", row=1, col=1)
    fig.update_xaxes(title_text="Time Index", row=1, col=2)
    fig.update_yaxes(title_text="Residuals", row=1, col=2)
    fig.update_xaxes(title_text="Fitted Values", row=2, col=1)
    fig.update_yaxes(title_text="√|Residuals|", row=2, col=1)
    fig.update_xaxes(title_text="Residuals", row=2, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=2)

    fig.show()
    fig.write_html(f"{title.lower().replace(' ', '_')}_diagnostics.html")


def interactive_currency_diagnostic_plots(results):
    """Interactive version of plot_currency_models"""
    currency = results['currency_name']
    residuals = results['residuals']
    predictions = results['predictions']

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Residuals vs Fitted Values (Linearity & Homoscedasticity)',
            'Residuals vs Time Index (Autocorrelation Check)',
            'Scale-Location Plot (Homoscedasticity)',
            'Histogram of Residuals'
        ],
        horizontal_spacing=0.08,
        vertical_spacing=0.1
    )

    # 1. Residuals vs Fitted
    fig.add_trace(
        go.Scatter(
            x=predictions,
            y=residuals,
            mode='markers',
            name='Residuals vs Fitted',
            marker=dict(color='blue', size=6, opacity=0.6),
            hovertemplate='Fitted: %{x:.3f}<br>Residual: %{y:.3f}<extra></extra>'
        ),
        row=1, col=1
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)

    # 2. Residuals vs Index
    fig.add_trace(
        go.Scatter(
            x=list(range(len(residuals))),
            y=residuals,
            mode='markers',
            name='Residuals vs Index',
            marker=dict(color='green', size=6, opacity=0.6),
            hovertemplate='Index: %{x}<br>Residual: %{y:.3f}<extra></extra>'
        ),
        row=1, col=2
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=2)

    # 3. Scale-Location Plot
    sqrt_abs_resid = np.sqrt(np.abs(residuals))
    fig.add_trace(
        go.Scatter(
            x=predictions,
            y=sqrt_abs_resid,
            mode='markers',
            name='Scale-Location',
            marker=dict(color='orange', size=6, opacity=0.6),
            hovertemplate='Fitted: %{x:.3f}<br>√|Residual|: %{y:.3f}<extra></extra>'
        ),
        row=2, col=1
    )

    # 4. Histogram of Residuals
    fig.add_trace(
        go.Histogram(
            x=residuals,
            name='Residuals Distribution',
            marker_color='purple',
            opacity=0.7,
            hovertemplate='Residual: %{x:.3f}<br>Count: %{y}<extra></extra>'
        ),
        row=2, col=2
    )

    fig.update_layout(
        title=f'{currency} Model - Interactive Diagnostic Plots',
        height=800,
        showlegend=False
    )

    # Update axis labels
    fig.update_xaxes(title_text="Fitted Values", row=1, col=1)
    fig.update_yaxes(title_text="Residuals", row=1, col=1)
    fig.update_xaxes(title_text="Time Index", row=1, col=2)
    fig.update_yaxes(title_text="Residuals", row=1, col=2)
    fig.update_xaxes(title_text="Fitted Values", row=2, col=1)
    fig.update_yaxes(title_text="√|Residuals|", row=2, col=1)
    fig.update_xaxes(title_text="Residuals", row=2, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=2)

    fig.show()
    fig.write_html(f"{currency.lower().replace(' ', '_')}_diagnostics.html")


def create_all_qq_plots(sp500_residuals, currency_results):
    """Create matplotlib subplot with all 6 QQ plots (S&P 500 + 5 currencies)"""
    from scipy import stats

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('QQ Plots - Normality Check for All Models',
                 fontsize=16, fontweight='bold')

    # Flatten axes for easier indexing
    axes_flat = axes.flatten()

    # S&P 500 QQ plot (first subplot)
    stats.probplot(sp500_residuals, dist="norm", plot=axes_flat[0])
    axes_flat[0].set_title('S&P 500 Model')
    axes_flat[0].grid(True, alpha=0.3)

    # Currency QQ plots
    currency_names = list(currency_results.keys())
    for i, name in enumerate(currency_names):
        if i < 5:  # Only plot first 5 currencies to fit in 2x3 grid
            residuals = currency_results[name]['residuals']
            stats.probplot(residuals, dist="norm", plot=axes_flat[i+1])
            axes_flat[i+1].set_title(f'{name} Model')
            axes_flat[i+1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('all_qq_plots.png', dpi=300, bbox_inches='tight')
    plt.show()


def interactive_qq_plot(residuals, title="QQ Plot of Residuals"):
    """Interactive version of create_qq_plot"""
    from scipy import stats

    # Generate theoretical quantiles
    theoretical_quantiles, ordered_values = stats.probplot(
        residuals, dist="norm", plot=None)

    fig = go.Figure()

    # Add scatter plot
    fig.add_trace(
        go.Scatter(
            x=theoretical_quantiles[0],
            y=theoretical_quantiles[1],
            mode='markers',
            name='Sample Quantiles',
            marker=dict(color='blue', size=6, opacity=0.7),
            hovertemplate='Theoretical: %{x:.3f}<br>Sample: %{y:.3f}<extra></extra>'
        )
    )

    # Add reference line
    slope, intercept = np.polyfit(
        theoretical_quantiles[0], theoretical_quantiles[1], 1)
    line_x = np.array([min(theoretical_quantiles[0]),
                      max(theoretical_quantiles[0])])
    line_y = slope * line_x + intercept

    fig.add_trace(
        go.Scatter(
            x=line_x,
            y=line_y,
            mode='lines',
            name='Reference Line',
            line=dict(color='red', width=2, dash='dash'),
            hovertemplate='Reference Line<extra></extra>'
        )
    )

    fig.update_layout(
        title=f'{title} (Interactive)<br><sub>Normality Check</sub>',
        xaxis_title='Theoretical Quantiles',
        yaxis_title='Sample Quantiles',
        height=600,
        showlegend=True
    )

    fig.show()
    fig.write_html(
        f"{title.lower().replace(' ', '_').replace(':', '').replace('-', '_')}.html")


# LEGACY MATPLOTLIB FUNCTIONS (kept for reference)
def plot_currency_models(results):
    """Create comprehensive diagnostic plots for currency models"""
    currency = results['currency_name']
    residuals = results['residuals']
    predictions = results['predictions']

    # Create subplot figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'{currency} Model - Diagnostic Plots', fontsize=16)

    # 1. Residuals vs Fitted (Linearity & Homoscedasticity)
    axes[0, 0].scatter(predictions, residuals, alpha=0.6)
    axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.8)
    axes[0, 0].set_xlabel('Fitted Values')
    axes[0, 0].set_ylabel('Residuals')
    axes[0, 0].set_title(
        'Residuals vs Fitted Values\n(Linearity & Homoscedasticity)')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Residuals vs Index (Autocorrelation)
    axes[0, 1].scatter(range(len(residuals)), residuals, alpha=0.6)
    axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.8)
    axes[0, 1].set_xlabel('Time Index')
    axes[0, 1].set_ylabel('Residuals')
    axes[0, 1].set_title('Residuals vs Time Index\n(Autocorrelation Check)')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Scale-Location Plot (Homoscedasticity)
    sqrt_abs_resid = np.sqrt(np.abs(residuals))
    axes[1, 0].scatter(predictions, sqrt_abs_resid, alpha=0.6)
    axes[1, 0].set_xlabel('Fitted Values')
    axes[1, 0].set_ylabel('√|Residuals|')
    axes[1, 0].set_title('Scale-Location Plot\n(Homoscedasticity)')
    axes[1, 0].grid(True, alpha=0.3)

    plt.tight_layout()


def create_sp500_diagnostic_plots(residuals, predictions, title="S&P 500 Model"):
    """Create comprehensive diagnostic plots for S&P 500 model"""

    # Create subplot figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'{title} - Diagnostic Plots', fontsize=16)

    # 1. Residuals vs Fitted (Linearity & Homoscedasticity)
    axes[0, 0].scatter(predictions, residuals, alpha=0.6)
    axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.8)
    axes[0, 0].set_xlabel('Fitted Values')
    axes[0, 0].set_ylabel('Residuals')
    axes[0, 0].set_title(
        'Residuals vs Fitted Values\n(Linearity & Homoscedasticity)')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Residuals vs Index (Autocorrelation)
    axes[0, 1].scatter(range(len(residuals)), residuals, alpha=0.6)
    axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.8)
    axes[0, 1].set_xlabel('Time Index')
    axes[0, 1].set_ylabel('Residuals')
    axes[0, 1].set_title('Residuals vs Time Index\n(Autocorrelation Check)')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Scale-Location Plot (Homoscedasticity)
    sqrt_abs_resid = np.sqrt(np.abs(residuals))
    axes[1, 0].scatter(predictions, sqrt_abs_resid, alpha=0.6)
    axes[1, 0].set_xlabel('Fitted Values')
    axes[1, 0].set_ylabel('√|Residuals|')
    axes[1, 0].set_title('Scale-Location Plot\n(Homoscedasticity)')
    axes[1, 0].grid(True, alpha=0.3)

    plt.tight_layout()


def create_qq_plot(residuals, title="QQ Plot of Residuals"):
    """Create a QQ plot for residuals (normality check)"""
    from scipy import stats
    plt.figure(figsize=(8, 6))
    stats.probplot(residuals, dist="norm", plot=plt)
    plt.title(f'{title}\n(Normality Check)')
    plt.grid(True)


def plot_feats(data):
    data['month_str'] = data['month'].astype(str)

    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    features = ['average_DiscountRate_value',
                'average_TreasurySecurities_value',
                'average_FedReserveBalanceSheet_value']

    for i, feat in enumerate(features):
        axes[i].plot(data["month_str"], data[feat])
        axes[i].set_title(
            f'{feat.replace("average_", "").replace("_value", "")} Over Time')
        axes[i].set_xlabel('Date')
        axes[i].set_ylabel(feat.replace("average_", "").replace("_value", ""))

        step = len(data) // 10
        axes[i].set_xticks(range(0, len(data), step))
        axes[i].set_xticklabels([data["month_str"].iloc[j] for j in range(0, len(data), step)],
                                rotation=45)
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_features_vs_sp500(data):
    """Plot each feature against S&P 500"""

    features = [
        'average_DiscountRate_value',
        'average_TreasurySecurities_value',
        'average_FedReserveBalanceSheet_value'
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Features vs S&P 500', fontsize=16)

    for i, feature in enumerate(features):
        clean_name = feature.replace('average_', '').replace('_value', '')

        axes[i].scatter(data[feature], data['close'], alpha=0.6)
        axes[i].set_xlabel(clean_name)
        axes[i].set_ylabel('S&P 500')
        axes[i].set_title(f'{clean_name} vs S&P 500')
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()


# Main execution starts here
if __name__ == "__main__":
    print("Starting financial data analysis with CSV caching...")

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

    # Load all currency data
    currencies = {
        "Euro": "Euro (EUR)",
        "Japanese Yen": "Japanese Yen (JPY)",
        "Australian Dollar": "Australian Dollar (AUD)",
        "Chinese Yuan": "Chinese Yuan (CNY)",
        "British Pound": "British Pound (GBP)"
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

    ''' # Apply square root transformation to Fed Reserve Balance Sheet
    merged_df['average_FedReserveBalanceSheet_value'] = np.sqrt(
        merged_df['average_FedReserveBalanceSheet_value'])'''

    plot_later = merged_df.copy()
    # Normalize full dataset
    data = normalize_full_df(merged_df)

    # S&P 500 Model
    X = np.ones((data.shape[0], 1))
    X = np.column_stack((X, data.drop(columns=['month', 'close']).values))
    y = np.array(data['close'])

    # Apply lag transformation to S&P 500 model
    X = X[1:]
    X = np.column_stack((X, y[:-1]))
    y = y[1:]

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

        X_currency, y_currency = create_currency_model(data, name)
        results = train_and_evaluate_currency_model(
            X_currency, y_currency, name)
        currency_results[name] = results

    # Print results
    print(f"\nS&P 500 Model:")
    print(f"  Full Dataset - R²: {r_squared_full:.4f}, MSE: {mse_full:.4f}")
    print(f"  Cross-Val    - R²: {sp500_cv_r2:.4f}, MSE: {sp500_cv_mse:.4f}")

    # INTERACTIVE PLOTS (NEW) - Creates HTML files for embedding
    print("\nCreating interactive plots...")

    interactive_plot_feats(plot_later)
    interactive_plot_features_vs_sp500(merged_df)
    interactive_sp500_diagnostic_plots(resids, ypreds_full, "S&P 500 Model")

    # Create single matplotlib subplot with all QQ plots
    create_all_qq_plots(resids, currency_results)

    for name, results in currency_results.items():
        interactive_currency_diagnostic_plots(results)
        print(f"\n{results['currency_name']} Model:")
        print(
            f"  Full Dataset - R²: {results['full_r2']:.4f}, MSE: {results['full_mse']:.4f}")
        print(
            f"  Cross-Val    - R²: {results['cv_r2']:.4f}, MSE: {results['cv_mse']:.4f}")

    print(
        f"\n{'Model':<15} {'Full R²':<10} {'Full MSE':<12} {'CV R²':<10} {'CV MSE':<12}")
    print("-" * 70)
    print(f"{'S&P 500':<15} {r_squared_full:<10.4f} {mse_full:<12.4f} {sp500_cv_r2:<10.4f} {sp500_cv_mse:<12.4f}")

    for name, results in currency_results.items():
        print(
            f"{name:<15} {results['full_r2']:<10.4f} {results['full_mse']:<12.4f} {results['cv_r2']:<10.4f} {results['cv_mse']:<12.4f}")

    num_cols = [col for col in data.columns if (data[col].dtype == float)]

    weights = {
        'SP500': vector_full,
        **{name: results['coefficients'] for name, results in currency_results.items()}
    }

    print("\nModel Weights:")
    for model, coeffs in weights.items():
        print(f"{model}: {coeffs}")

    print("\nInteractive HTML files created for embedding in Markdown:")
    print("- features_over_time.html")
    print("- features_vs_sp500.html")
    print("- s&p_500_model_diagnostics.html")
    print("- s&p_500_model_qq_plot_of_residuals.html")
    print("- [currency]_diagnostics.html (for each currency)")
    print("- [currency]_model_qq_plot_of_residuals.html (for each currency)")
