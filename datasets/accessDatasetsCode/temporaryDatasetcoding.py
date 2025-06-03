from FREDData import interestRate as ir
import pandas as pd
from yahoofinance import monthly_sp500
import numpy as np
from sklearn.metrics import r2_score
import plotly.express as px
import plotly.graph_objects as go
from FREDData import conversions as cr


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


# Data loading and processing
map = {
    "DiscountRate": "INTDSRUSM193N",
    "TreasurySecurities": "WSHOMCB",
    "FedReserveBalanceSheet": "WALCL"
}

dfs_to_concat = []

for key in map.keys():
    dfs_to_concat.append(ir(key))

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

euros = cr("Euro (EUR)")

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

merged_df2 = pd.merge(merged_df, euros, how="inner", on="month")
data_currency = normalize_full_df(merged_df2)

data_currency = data_currency[data_currency['average_TreasurySecurities_value'] > .2]

# Full dataset regression for residual plots
X = np.ones((data.shape[0], 1))
X = np.column_stack((X, data.drop(columns=['month', 'close']).values))
y = np.array(data['close'])

vector_full = regress(X, y)
ypreds_full = np.dot(X, vector_full)
resids = ypreds_full - y

mse_full = np.mean((ypreds_full - y) ** 2)
print("Full dataset Mean Squared Error:", mse_full)
r_squared_full = r2_score(y, ypreds_full)
print("Full dataset R²:", r_squared_full)

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


def plot_feats_2():
    print(data_currency)
    currency_feats = data_currency.drop(columns=['month', 'exchange_value'])
    for col in currency_feats.columns:
        fig = px.scatter(
            x=currency_feats[col],
            y=data_currency['exchange_value'],
            title=f'Currency V.S {col}',
            labels={'x': col, 'y': 'ExchangeRate'}
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.write_html(f'Currency_{col}.html')
        fig.show()


plot()
# plot_feats_1()
# plot_feats_no_normal()
