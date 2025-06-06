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
    "CAN": "Canada",
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


def create_sophisticated_gdp_lag(df, gdp_col='GDP_per_capita', lag_years=1):
    df = df.copy()
    df['date'] = pd.to_numeric(df['date'])
    df = df.sort_values(['Country', 'date'])
    

    df[f'{gdp_col}_lag{lag_years}'] = df.groupby('Country')[gdp_col].shift(lag_years)
    

    gdp_based_features = ['Health_spending', 'Education_spending']
    
    for feature in gdp_based_features:
        if feature in df.columns:
            current_spending_amount = (df[feature] / 100) * df[gdp_col]  
            df[f'{feature}_lag{lag_years}'] = (current_spending_amount / df[f'{gdp_col}_lag{lag_years}']) * 100
    

    if 'Military Spending' in df.columns:
        df[f'Military Spending_lag{lag_years}'] = df.groupby('Country')['Military Spending'].shift(lag_years)
    

    df = df.drop(columns=[f'{gdp_col}_lag{lag_years}'])
    
    return df



govt_health = fetch_worldbank_data("SH.XPD.CHEX.GD.ZS") 
govt_education = fetch_worldbank_data("SE.XPD.TOTL.GD.ZS") 
military_spending = fetch_worldbank_data("MS.MIL.XPND.ZS")
gdp_per_capita = fetch_worldbank_data("NY.GDP.PCAP.CD")


df = gdp_per_capita.rename(columns={'value': 'GDP_per_capita'})
df = df.merge(govt_health.rename(columns={'value': 'Health_spending'}), on=[
    'Country', 'date'], how='outer')
df = df.merge(govt_education.rename(
    columns={'value': 'Education_spending'}), on=['Country', 'date'], how='outer')
df = df.merge(military_spending.rename(columns={'value': 'Military Spending'}), on=[
    'Country', 'date'], how='inner')


df = create_sophisticated_gdp_lag(df, gdp_col='GDP_per_capita', lag_years=1)

df['date'] = pd.to_numeric(df['date'])
df['previous_year'] = df['date'] - 1




features_to_lag = ['Health_spending', 'Education_spending', 'Military Spending']
lagged_features = [f'{feature}_lag1' for feature in features_to_lag]
model_data = df.dropna(subset=['GDP_per_capita'] + lagged_features + ['previous_year'])




for i, feature in enumerate(lagged_features):
    original_feature = features_to_lag[i]
    plot_data = model_data.dropna(subset=[feature, 'GDP_per_capita'])

    

    if len(plot_data) > 0:
        if 'Military' in feature:
            label_suffix = "(Previous Year)"
        else:
            label_suffix = "(Current Spending as % of Previous Year's GDP)"
            
        fig = px.scatter(
            plot_data,
            x=feature,
            y='GDP_per_capita',
            color='Country',
            hover_data=['date'],
            labels={
                feature: f'{original_feature.replace("_", " ").title()} {label_suffix}',
                'GDP_per_capita': 'GDP per Capita (USD)'
            },
            title=f'{original_feature.replace("_", " ").title()} {label_suffix} vs Current GDP per Capita ({len(plot_data)} points)'
        )
        
        fig.update_traces(marker=dict(size=10))
        fig.show()


def regress(X, y):
    
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


numeric_cols = ['GDP_per_capita'] + lagged_features + ['previous_year']
for col in numeric_cols:
    model_data[col] = pd.to_numeric(model_data[col], errors='coerce')

model_data = model_data.dropna(subset=numeric_cols)

country_dummies = pd.get_dummies(model_data['Country'], prefix='Country')
model_data = pd.concat([model_data, country_dummies], axis=1)
model_data = model_data.drop(columns=['Country'])


model_data = normalize_features(model_data)


columns_to_use = lagged_features + ['previous_year'] + [col for col in model_data.columns if col.startswith('Country_')]
X = model_data[columns_to_use].astype(np.float64).values
X = np.column_stack([np.ones(len(X)), X])
y = model_data['GDP_per_capita'].astype(np.float64).values






if np.any(np.isnan(X)) or np.any(np.isinf(X)):
    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

if np.any(np.isnan(y)) or np.any(np.isinf(y)):
    y = np.nan_to_num(y, nan=0.0, posinf=1e6, neginf=-1e6)

b = regress(X, y)
ypreds = np.dot(X, b)

r2 = r2_score(y, ypreds)
mse = mean_squared_error(y, ypreds)







X_raw = model_data[columns_to_use].astype(np.float64).values
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


import matplotlib.pyplot as plt


original_model_data = df.dropna(subset=['GDP_per_capita'] + lagged_features + ['previous_year'])
original_model_data = original_model_data.reset_index(drop=True)


country_dummies_original = pd.get_dummies(original_model_data['Country'], prefix='Country')
original_with_dummies = pd.concat([original_model_data, country_dummies_original], axis=1)





for i, feature in enumerate(lagged_features + ['previous_year']):
    
    
    X_feature_values = original_model_data[feature].values
    y_values = original_model_data['GDP_per_capita'].values
    
    
    country_cols = [col for col in country_dummies_original.columns]
    
    
    X_feature_only = X_feature_values.reshape(-1, 1)
    X_countries = country_dummies_original.values
    
    
    X_combined = np.column_stack([
        np.ones(len(X_feature_values)),  
        X_feature_values,                
        X_countries                      
    ])
    
    
    valid_mask = ~(np.isnan(X_combined).any(axis=1) | np.isnan(y_values) | 
                   np.isinf(X_combined).any(axis=1) | np.isinf(y_values))
    
    X_combined_clean = X_combined[valid_mask]
    y_clean = y_values[valid_mask]
    X_feature_values_clean = X_feature_values[valid_mask]
    
    if len(X_combined_clean) == 0:
        
        continue
    
    
    b_feature_country = regress(X_combined_clean, y_clean)
    y_pred_feature_country = np.dot(X_combined_clean, b_feature_country)
    
    
    resids_feature = y_clean - y_pred_feature_country
    
    
    if feature == 'previous_year':
        plot_title = 'Previous Year'
        x_label = 'Previous Year'
    else:
        original_name = feature.replace('_lag1', '').replace('_', ' ').title()
        if 'Health' in original_name:
            plot_title = 'Health Spending'
            x_label = 'Health Spending (Current as % of Previous GDP)'
        elif 'Education' in original_name:
            plot_title = 'Education Spending'
            x_label = 'Education Spending (Current as % of Previous GDP)'
        elif 'Military' in original_name:
            plot_title = 'Military Spending'
            x_label = 'Military Spending (% of GDP)'
        else:
            plot_title = original_name
            x_label = original_name
    
    
    plt.figure(figsize=(10, 6))
    
    
    countries_clean = original_model_data['Country'].values[valid_mask]
    unique_countries = np.unique(countries_clean)
    colors = plt.cm.Set1(np.linspace(0, 1, len(unique_countries)))
    
    for j, country in enumerate(unique_countries):
        mask = countries_clean == country
        plt.scatter(X_feature_values_clean[mask], resids_feature[mask], 
                   alpha=0.7, s=60, label=country, color='black')
    
    plt.xlabel(x_label)
    plt.ylabel('Residuals (Country-Adjusted)')
    plt.title(f'Residual Plot vs. X Values - {plot_title}')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    
    
    plt.figure(figsize=(10, 6))
    for j, country in enumerate(unique_countries):
        mask = countries_clean == country
        indices = np.where(mask)[0]
        plt.scatter(indices, resids_feature[mask], 
                   alpha=0.7, s=60, label=country, color='black')
    
    plt.xlabel(f'Index')
    plt.ylabel('Residuals (Country-Adjusted)')
    plt.title(f'Residual Plot vs. Order - {plot_title}')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    
    
    r2_feature = r2_score(y_clean, y_pred_feature_country)
    mse_feature = mean_squared_error(y_clean, y_pred_feature_country)
    
    
    
    
    
    
    
    
    
    
    
    
    feature_coef = b_feature_country[1]  
    














correlation_comparison = pd.DataFrame()

df_temp = df.copy()
df_temp['date'] = pd.to_numeric(df_temp['date'])
df_temp = df_temp.sort_values(['Country', 'date'])