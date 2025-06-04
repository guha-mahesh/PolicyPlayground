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


govt_health = fetch_worldbank_data("SH.XPD.CHEX.GD.ZS") # % of gdp
govt_education = fetch_worldbank_data("SE.XPD.TOTL.GD.ZS") # % of gdp
# Air transport passengers - infrastructure policy proxy
# Military Spending
military_spending = fetch_worldbank_data("MS.MIL.XPND.ZS")

# IE.PPI.ENGY.CD - education
# MS.MIL.XPND.ZS - military (% of general government expenditure)

# Economic prosperity measure
gdp_per_capita = fetch_worldbank_data("NY.GDP.PCAP.CD")

# Merge data

df = gdp_per_capita.rename(columns={'value': 'GDP_per_capita'})
df = df.merge(govt_health.rename(columns={'value': 'Health_spending'}), on=[
    'Country', 'date'], how='outer')
df = df.merge(govt_education.rename(
    columns={'value': 'Education_spending'}), on=['Country', 'date'], how='outer')
df = df.merge(military_spending.rename(columns={'value': 'Military Spending'}), on=[
    'Country', 'date'], how='inner')

model_data = df.dropna(
    subset=['GDP_per_capita', 'Health_spending', 'Education_spending', 'Military Spending'])


features = ['Health_spending', 'Education_spending', 'Military Spending']

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
    # `X and y are numeric arrays
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    dot1 = np.dot(X.T, X)

    regularization = 1e-8 * np.eye(dot1.shape[0])
    dot1_reg = dot1 + regularization

    try:
        inv = np.linalg.inv(dot1_reg)
    except np.linalg.LinAlgError:
        inv = np.linalg.pinv(dot1)

    dot2 = np.dot(X.T, y)
    return np.dot(inv, dot2)


def normalize_features(df):
    df = df.copy()
    for col in df.columns:
        if col == "date" or col.startswith('Country_'):
            continue

        values = df[col].astype(np.float64)

        if (values >= 0).all() and values.max() > 1000:
            values = np.log1p(values)

        std = values.std()
        if std != 0:
            df[col] = (values - values.mean()) / std
        else:
            df[col] = 0
    return df


numeric_cols = ['GDP_per_capita', 'Health_spending',
                'Education_spending', 'Military Spending']
for col in numeric_cols:
    model_data[col] = pd.to_numeric(model_data[col], errors='coerce')


model_data = model_data.dropna(subset=numeric_cols)


country_dummies = pd.get_dummies(model_data['Country'], prefix='Country')
model_data = pd.concat([model_data, country_dummies], axis=1)
model_data = model_data.drop(columns=['Country'])


model_data = normalize_features(model_data)


X = model_data.drop(columns=['date', 'GDP_per_capita']).astype(
    np.float64).values
X = np.column_stack([np.ones(len(X)), X])
y = model_data['GDP_per_capita'].astype(np.float64).values

print(f"X shape: {X.shape}, X dtype: {X.dtype}")
print(f"y shape: {y.shape}, y dtype: {y.dtype}")


if np.any(np.isnan(X)) or np.any(np.isinf(X)):
    # print("Warning: X contains NaN or inf values")
    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

if np.any(np.isnan(y)) or np.any(np.isinf(y)):
    # print("Warning: y contains NaN or inf values")
    y = np.nan_to_num(y, nan=0.0, posinf=1e6, neginf=-1e6)


b = regress(X, y)
ypreds = np.dot(X, b)

r2 = r2_score(y, ypreds)
mse = mean_squared_error(y, ypreds)

print(f"\nMODEL RESULTS (WITH ONE-HOT ENCODED COUNTRIES)")
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


resids = y - ypreds
print(f"\nResiduals summary:")
print(f"Mean: {np.mean(resids):.6f}")
print(f"Std: {np.std(resids):.4f}")
print(f"Min: {np.min(resids):.4f}")
print(f"Max: {np.max(resids):.4f}")

feature_names = list(model_data.drop(
    columns=['date', 'GDP_per_capita']).columns)
coefficients = b[1:]
feature_importance = pd.DataFrame({
    'Feature': feature_names,
    'Coefficient': coefficients,
    'Abs_Coefficient': np.abs(coefficients)
}).sort_values('Abs_Coefficient', ascending=False)


print("HEAD OF MAIN DATASET (df)")
print(df.head())
print(f"Shape: {df.shape}")


print("\nHEAD OF MODEL DATA")
print(model_data.head())
print(f"Shape: {model_data.shape}")

print("\nFEATURE IMPORTANCE RESULTS")
print(feature_importance.head(10))



df['date_numeric'] = pd.to_numeric(df['date'])

# Create individual time series plots for each metric
metrics = {
    'GDP_per_capita': 'GDP per Capita (USD)',
    'Health_spending': 'Health Spending (% of GDP)', 
    'Education_spending': 'Education Spending (% of GDP)',
    'Military Spending': 'Military Spending (% of general government expenditure)'
}

for metric, title in metrics.items():
    plot_data = df.dropna(subset=[metric])
    
    if len(plot_data) > 0:
        fig = px.line(
            plot_data,
            x='date_numeric',
            y=metric,
            color='Country',
            markers=True,
            title=f'{title} Over Time by Country',
            labels={
                'date_numeric': 'Year',
                metric: title
            }
        )
        
        fig.update_layout(
            xaxis_title='Year',
            yaxis_title=title,
            legend_title='Country',
            hovermode='x unified'
        )
        

        fig.update_xaxes(
            tickmode='linear',
            tick0=2010,
            dtick=1
        )
        
        fig.show()
        
        print(f"\n{title} Summary")
        summary = plot_data.groupby('Country')[metric].agg(['mean', 'std', 'min', 'max']).round(2)
        print(summary)

from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=list(metrics.values()),
    specs=[[{"secondary_y": False}, {"secondary_y": False}],
           [{"secondary_y": False}, {"secondary_y": False}]]
)

row_col_mapping = [(1,1), (1,2), (2,1), (2,2)]

for i, (metric, title) in enumerate(metrics.items()):
    row, col = row_col_mapping[i]
    plot_data = df.dropna(subset=[metric])
    
    for country in plot_data['Country'].unique():
        country_data = plot_data[plot_data['Country'] == country]
        fig.add_scatter(
            x=country_data['date_numeric'],
            y=country_data[metric],
            mode='lines+markers',
            name=country,
            legendgroup=country,
            showlegend=(i == 0),
            row=row, col=col
        )

fig.update_layout(
    height=800,
    title_text="All Metrics Over Time by Country",
    hovermode='x unified'
)

for i in range(1, 5):
    fig.update_xaxes(
        tickmode='linear',
        tick0=2010,
        dtick=2,
        title_text='Year',
        row=(i-1)//2 + 1,
        col=(i-1)%2 + 1
    )

fig.show()

# Calculate correlation between time and each metric by country
print("\n=== TIME TREND CORRELATIONS ===")
print("Correlation between Year and each metric by country:")
print("(Positive = increasing over time, Negative = decreasing over time)")

for metric in metrics.keys():
    print(f"\n{metric}:")
    correlations = df.dropna(subset=[metric]).groupby('Country').apply(
        lambda x: x['date_numeric'].corr(x[metric])
    ).round(3)
    print(correlations)

# Identify strongest trends
print("\n=== STRONGEST TRENDS ===")
for metric in metrics.keys():
    metric_data = df.dropna(subset=[metric])
    correlations = metric_data.groupby('Country').apply(
        lambda x: x['date_numeric'].corr(x[metric])
    )
    
    strongest_pos = correlations.idxmax() if correlations.max() > 0.5 else None
    strongest_neg = correlations.idxmin() if correlations.min() < -0.5 else None
    
    print(f"\n{metric}:")
    if strongest_pos:
        print(f"  Strongest increasing trend: {strongest_pos} (r={correlations[strongest_pos]:.3f})")
    if strongest_neg:
        print(f"  Strongest decreasing trend: {strongest_neg} (r={correlations[strongest_neg]:.3f})")
    if not strongest_pos and not strongest_neg:
        print(f"  No strong trends (all correlations between -0.5 and 0.5)")
