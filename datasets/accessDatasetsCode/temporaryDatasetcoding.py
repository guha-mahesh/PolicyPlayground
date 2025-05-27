from FREDData import interestRate as ir
import pandas as pd
from FREDData import exports as ex
from yahoofinance import monthly_sp500
import numpy as np
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
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


map = {

    "DiscountRate": "INTDSRUSM193N",
    "TreasurySecurities": "WSHOMCB",
    "FedReserveBalanceSheet": "WALCL"

}


dfs_to_concat = []

for key in map.keys():
    dfs_to_concat.append(ir(key))

exports_df = ex()
dfs_to_concat.append(exports_df)

dfs = [clean_data(df) for df in dfs_to_concat]
new_dfs = standardize_dates(dfs)
normalized = []


final_dfs = []
for df in new_dfs:
    final_dfs.append(find_averages(df))


sandp = monthly_sp500()


merged_df = final_dfs[0]

for df in final_dfs[1:]:
    merged_df = pd.merge(merged_df, df, how="inner", on="month")
merged_df = pd.merge(merged_df, sandp, how="inner", on="month")


euros = cr("Euro (EUR)")

data = normalize_full_df(merged_df)
data = data[(data['average_exports_value'] < 0) &
            (data['average_TreasurySecurities_value'] > -1)]

merged_df2 = pd.merge(merged_df, euros, how="inner", on="month")
data_currency = normalize_full_df(merged_df2)


X = np.ones((data.shape[0], 1))
X = np.column_stack((X, data.drop(columns=['month', 'close']).values))
y = np.array(data['close'])


def regress(X, y):
    dot1 = np.dot(X.T, X)
    inv = np.linalg.inv(dot1)
    dot2 = np.dot(X.T, y)
    return np.dot(inv, dot2)


vector = regress(X, y)
ypreds = np.dot(X, vector)

resids = ypreds-y


mse = np.mean((ypreds - y) ** 2)
print("Mean Squared Error:", mse)
r_squared = r2_score(y, ypreds)
print("R²:", r_squared)


num_cols = [col for col in data.columns if (
    data[col].dtype == float)]


def plot():
    for col in num_cols:
        lst = data[col].tolist()
        plt.figure()
        plt.scatter(lst, resids, label=col)
        plt.legend()


def plot_feats_1():
    data2 = data.drop(columns=['month', 'close'])
    for col in data2.columns:
        plt.figure()
        plt.scatter(data2[col].tolist(), data['close'].tolist())
        plt.title(f'The S&P 500 index V.S {col} ')
        plt.savefig(f'The_S&P_500_index_V.S_{col}.png')
        plt.xlabel(col)
        plt.ylabel('The S&P 500')


def plot_feats_2():
    print(data_currency)
    currency_feats = data_currency.drop(columns=['month', 'exchange_value'])
    for col in currency_feats.columns:
        plt.figure()
        plt.scatter(currency_feats[col].tolist(),
                    data_currency['exchange_value'].tolist())
        plt.title(f'Currency V.S {col} ')
        plt.savefig(f'Currency_{col}.png')
        plt.xlabel(col)
        plt.ylabel('ExchangeRate')


plot_feats_2()
plt.show()
