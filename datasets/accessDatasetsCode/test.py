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


# Government direct controls - absolute spending amounts and policy measures
# Total government health expenditure (absolute dollars)
# Current health expenditure, government (current US$)
govt_health_total = fetch_worldbank_data("SH.XPD.GHED.CD")

# Total government education expenditure (absolute dollars)
# Government expenditure on education, total (current US$)
govt_education_total = fetch_worldbank_data("SE.XPD.TOTL.CD")

# Government infrastructure/capital spending
# General government final consumption expenditure (current US$)
govt_infrastructure = fetch_worldbank_data("NE.CON.GOVT.CD")
# This includes infrastructure, public services, defense - all direct government spending

# Alternative infrastructure measure - you could also use:
# "GC.XPN.TOTL.CD" - Expense (current US$) - total government operational spending
# "GC.REV.TOTL.CD" - Revenue, total (current US$) - government's fiscal capacity

# Economic prosperity measure
gdp_per_capita = fetch_worldbank_data("NY.GDP.PCAP.CD")

# Additional government control variables you could add:
# Government debt: "GC.DOD.TOTL.CD" - Central government debt, total (current US$)
# Military spending: "MS.MIL.XPND.CD" - Military expenditure (current US$)
# Tax revenue: "GC.TAX.TOTL.CD" - Tax revenue (current US$)

# Merge data
df = gdp_per_capita.rename(columns={'value': 'GDP_per_capita'})
df = df.merge(govt_health_total.rename(columns={'value': 'Govt_Health_Total'}), on=[
    'Country', 'date'], how='outer')
df = df.merge(govt_education_total.rename(
    columns={'value': 'Govt_Education_Total'}), on=['Country', 'date'], how='outer')
df = df.merge(govt_infrastructure.rename(columns={'value': 'Govt_Infrastructure_Total'}), on=[
    'Country', 'date'], how='outer')

model_data = df.dropna(
    subset=['GDP_per_capita', 'Govt_Health_Total', 'Govt_Education_Total', 'Govt_Infrastructure_Total'])


# Plot each feature against GDP per capita (BEFORE normalization)
features = ['Govt_Health_Total',
            'Govt_Education_Total', 'Govt_Infrastructure_Total']

for feature in features:

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
    # Ensure X and y are numeric arrays
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    dot1 = np.dot(X.T, X)

    # Add regularization to handle potential singularity
    regularization = 1e-8 * np.eye(dot1.shape[0])
    dot1_reg = dot1 + regularization

    try:
        inv = np.linalg.inv(dot1_reg)
    except np.linalg.LinAlgError:
        # Use pseudo-inverse if regular inverse fails
        inv = np.linalg.pinv(dot1)

    dot2 = np.dot(X.T, y)
    return np.dot(inv, dot2)


def normalize_features(df):
    df = df.copy()
    for col in df.columns:
        if col == "date" or col.startswith('Country_'):
            continue

        values = df[col].astype(np.float64)  # Ensure numeric type

        if (values >= 0).all() and values.max() > 1000:
            values = np.log1p(values)

        std = values.std()
        if std != 0:
            df[col] = (values - values.mean()) / std
        else:
            df[col] = 0  # If constant column, set to 0
    return df


numeric_cols = ['GDP_per_capita', 'Govt_Health_Total',
                'Govt_Education_Total', 'Govt_Infrastructure_Total']
for col in numeric_cols:
    model_data[col] = pd.to_numeric(model_data[col], errors='coerce')


model_data = model_data.dropna(subset=numeric_cols)


country_dummies = pd.get_dummies(model_data['Country'], prefix='Country')
model_data = pd.concat([model_data, country_dummies], axis=1)
model_data = model_data.drop(columns=['Country'])


model_data = normalize_features(model_data)


X = model_data.drop(columns=['date', 'GDP_per_capita']).astype(
    np.float64).values
X = np.column_stack([np.ones(len(X)), X])  # Add intercept
y = model_data['GDP_per_capita'].astype(np.float64).values

print(f"X shape: {X.shape}, X dtype: {X.dtype}")
print(f"y shape: {y.shape}, y dtype: {y.dtype}")


if np.any(np.isnan(X)) or np.any(np.isinf(X)):
    print("Warning: X contains NaN or inf values")
    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

if np.any(np.isnan(y)) or np.any(np.isinf(y)):
    print("Warning: y contains NaN or inf values")
    y = np.nan_to_num(y, nan=0.0, posinf=1e6, neginf=-1e6)


b = regress(X, y)
ypreds = np.dot(X, b)

r2 = r2_score(y, ypreds)
mse = mean_squared_error(y, ypreds)

print(f"\n=== MODEL RESULTS (WITH ONE-HOT ENCODED COUNTRIES) ===")
print(f"R² Score: {r2:.4f}")
print(f"MSE: {mse:.4f}")
print(f"Number of observations: {len(y)}")
print(f"Number of features (including countries): {X.shape[1] - 1}")


X_raw = model_data.drop(
    columns=['date', 'GDP_per_capita']).astype(np.float64).values
y_raw = model_data['GDP_per_capita'].astype(np.float64).values

X_train_raw, X_test_raw, y_train_raw, y_test_raw = train_test_split(
    X_raw, y_raw, test_size=0.3, random_state=42
)

X_train = np.column_stack([np.ones(len(X_train_raw)), X_train_raw])
X_test = np.column_stack([np.ones(len(X_test_raw)), X_test_raw])
y_train = y_train_raw
y_test = y_test_raw

b_train = regress(X_train, y_train)
ypreds_test = np.dot(X_test, b_train)
r2_test = r2_score(y_test, ypreds_test)
print(f"Test set R² score: {r2_test:.4f}")

# Residuals
resids = y - ypreds
print(f"\nResiduals summary:")
print(f"Mean: {np.mean(resids):.6f}")
print(f"Std: {np.std(resids):.4f}")
print(f"Min: {np.min(resids):.4f}")
print(f"Max: {np.max(resids):.4f}")

# Feature importance (absolute values of coefficients, excluding intercept)
feature_names = list(model_data.drop(
    columns=['date', 'GDP_per_capita']).columns)
coefficients = b[1:]  # Exclude intercept
feature_importance = pd.DataFrame({
    'Feature': feature_names,
    'Coefficient': coefficients,
    'Abs_Coefficient': np.abs(coefficients)
}).sort_values('Abs_Coefficient', ascending=False)

print(f"\n=== FEATURE IMPORTANCE ===")
print(feature_importance)
