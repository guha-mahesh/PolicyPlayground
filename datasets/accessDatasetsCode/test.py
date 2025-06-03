import pandas as pd
import requests
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error
import plotly.express as px
from sklearn.model_selection import train_test_split

country_code_to_name = {
    "USA": "United States",
    "JPN": "Japan",
    "DEU": "Germany",
    "GBR": "United Kingdom",
    "FRA": "France",
    "RUS": "Russia",
    "CAN": "Canada"
}


def fetch_worldbank_data(indicator, start_year=2010, end_year=2023):
    url = (
        f"https://api.worldbank.org/v2/country/"
        f"{';'.join(country_code_to_name.keys())}/indicator/{indicator}"
        f"?format=json&per_page=500&date={start_year}:{end_year}"
    )
    response = requests.get(url).json()
    if len(response) < 2:
        return pd.DataFrame()
    data = response[1]
    df = pd.json_normalize(data)
    df = df[['countryiso3code', 'date', 'value']]
    df['Country'] = df['countryiso3code'].map(country_code_to_name)
    df['date'] = df['date'].astype(str)
    df = df.drop('countryiso3code', axis=1)
    return df


# Direct government policy controls
govt_health = fetch_worldbank_data("SH.XPD.CHEX.GD.ZS")
govt_education = fetch_worldbank_data("SE.XPD.TOTL.GD.ZS")
# Air transport passengers - infrastructure policy proxy
infrastructure_spending = fetch_worldbank_data("IS.AIR.PSGR")

# Economic prosperity measure
gdp_per_capita = fetch_worldbank_data("NY.GDP.PCAP.CD")

# Merge data
df = gdp_per_capita.rename(columns={'value': 'GDP_per_capita'})
df = df.merge(govt_health.rename(columns={'value': 'Health_spending'}), on=[
    'Country', 'date'], how='outer')
df = df.merge(govt_education.rename(
    columns={'value': 'Education_spending'}), on=['Country', 'date'], how='outer')
df = df.merge(infrastructure_spending.rename(columns={'value': 'Infrastructure_proxy'}), on=[
    'Country', 'date'], how='outer')

model_data = df.dropna(
    subset=['GDP_per_capita', 'Health_spending', 'Education_spending', 'Infrastructure_proxy'])

print(f"=== DATA AVAILABILITY CHECK ===")
print(f"Total data points with all features: {len(model_data)}")
print(f"Countries represented: {model_data['Country'].nunique()}")
print(f"Years covered: {sorted(model_data['date'].unique())}")

# Plot each feature against GDP per capita (BEFORE normalization)
features = ['Health_spending', 'Education_spending', 'Infrastructure_proxy']

for feature in features:
    # Use original data for plotting (before normalization)
    plot_data = df.dropna(subset=[feature, 'GDP_per_capita'])

    print(f"\n{feature} vs GDP: {len(plot_data)} data points")

    if len(plot_data) > 0:
        fig = px.scatter(
            plot_data,
            x=feature,
            y='GDP_per_capita',
            color='Country',
            hover_data=['date'],
            labels={
                feature: feature.replace('_', ' ').title(),
                'GDP_per_capita': 'GDP per Capita (USD)'
            },
            title=f'{feature.replace("_", " ").title()} vs GDP per Capita ({len(plot_data)} points)'
        )
        fig.show()


def regress(X, y):
    dot1 = np.dot(X.T, X)
    inv = np.linalg.inv(dot1)
    dot2 = np.dot(X.T, y)
    return np.dot(inv, dot2)


def normalize_full_df(df):
    df = df.copy()
    for col in df.columns:
        if col == "date" or col == "Country":
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


# Split BEFORE normalization
X_raw = model_data[['Health_spending',
                    'Education_spending', 'Infrastructure_proxy']]
y_raw = model_data['GDP_per_capita']

X_train_raw, X_test_raw, y_train_raw, y_test_raw = train_test_split(
    X_raw, y_raw, test_size=0.3, random_state=42
)

# Normalize train and test separately
train_data = pd.concat([X_train_raw, y_train_raw], axis=1)
test_data = pd.concat([X_test_raw, y_test_raw], axis=1)

train_norm = normalize_full_df(train_data)
test_norm = normalize_full_df(test_data)

X_train = np.column_stack([np.ones(len(train_norm)), train_norm[[
    'Health_spending', 'Education_spending', 'Infrastructure_proxy']].values])
X_test = np.column_stack([np.ones(len(test_norm)), test_norm[[
    'Health_spending', 'Education_spending', 'Infrastructure_proxy']].values])
y_train = train_norm['GDP_per_capita'].values
y_test = test_norm['GDP_per_capita'].values

# Original model (full data normalized together)
model_data = normalize_full_df(model_data)
X = np.ones((model_data.shape[0], 1))
X = np.column_stack((X, model_data.drop(columns=['date', 'Country']).values))
y = np.array(model_data['GDP_per_capita'])

b = regress(X, y)
ypreds = np.dot(X, b)

r2 = r2_score(y, ypreds)
mse = mean_squared_error(y, ypreds)

print(f"\n=== MODEL RESULTS ===")
print(f"R² Score: {r2:.4f}")
print(f"MSE: {mse:.4f}")
print(f"Number of observations: {len(y)}")
print(f"Number of features: {X.shape[1] - 1}")

b_train = regress(X_train, y_train)
ypreds_train = np.dot(X_test, b_train)
r2_train = r2_score(y_test, ypreds_train)
print(f"r2 score: {r2_train}")
