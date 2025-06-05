import pandas as pd
import numpy as np
import requests
from sklearn.metrics import r2_score


gdp_model_coefficients = None
gdp_feature_means = {}
gdp_feature_stds = {}
gdp_country_features = []
gdp_log_transformed_features = set()

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


def create_sophisticated_gdp_lag(df, gdp_col='GDP_per_capita', lag_years=1):
    df = df.copy()
    df['date'] = pd.to_numeric(df['date'])
    df = df.sort_values(['Country', 'date'])

    df[f'{gdp_col}_lag{lag_years}'] = df.groupby(
        'Country')[gdp_col].shift(lag_years)

    gdp_based_features = ['Health_spending', 'Education_spending']

    for feature in gdp_based_features:
        if feature in df.columns:
            current_spending_amount = (df[feature] / 100) * df[gdp_col]
            df[f'{feature}_lag{lag_years}'] = (
                current_spending_amount / df[f'{gdp_col}_lag{lag_years}']) * 100

    if 'Military Spending' in df.columns:
        df[f'Military Spending_lag{lag_years}'] = df.groupby(
            'Country')['Military Spending'].shift(lag_years)

    df = df.drop(columns=[f'{gdp_col}_lag{lag_years}'])
    return df


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


def normalize_features(df, feature_means=None, feature_stds=None, log_features=None, fit=False):
    global gdp_log_transformed_features
    df = df.copy()

    if fit:
        means = {}
        stds = {}
        log_features = set()
    else:
        means = feature_means
        stds = feature_stds
        log_features = log_features or set()

    for col in df.columns:
        if col == "date" or col.startswith('Country_'):
            continue

        values = df[col].astype(np.float64)

        if fit:
            if (values >= 0).all() and values.max() > 1000:
                values = np.log1p(values)
                log_features.add(col)
        else:
            if col in log_features:
                values = np.log1p(values)

        if fit:
            mean_val = values.mean()
            std_val = values.std()
            means[col] = mean_val
            stds[col] = std_val
        else:
            mean_val = means.get(col, 0)
            std_val = stds.get(col, 1)

        if std_val != 0:
            df[col] = (values - mean_val) / std_val
        else:
            df[col] = 0

    if fit:
        gdp_log_transformed_features = log_features
        return df, means, stds
    else:
        return df


def prepare_training_data():

    govt_health = fetch_worldbank_data("SH.XPD.CHEX.GD.ZS")
    govt_education = fetch_worldbank_data("SE.XPD.TOTL.GD.ZS")
    military_spending = fetch_worldbank_data("MS.MIL.XPND.ZS")
    gdp_per_capita = fetch_worldbank_data("NY.GDP.PCAP.CD")

    df = gdp_per_capita.rename(columns={'value': 'GDP_per_capita'})
    df = df.merge(govt_health.rename(columns={'value': 'Health_spending'}), on=[
                  'Country', 'date'], how='outer')
    df = df.merge(govt_education.rename(
        columns={'value': 'Education_spending'}), on=['Country', 'date'], how='outer')
    df = df.merge(military_spending.rename(
        columns={'value': 'Military Spending'}), on=['Country', 'date'], how='inner')

    df = create_sophisticated_gdp_lag(
        df, gdp_col='GDP_per_capita', lag_years=1)
    df['date'] = pd.to_numeric(df['date'])
    df['previous_year'] = df['date'] - 1

    return df


def train_gdp_model():
    global gdp_model_coefficients, gdp_feature_means, gdp_feature_stds, gdp_country_features

    df = prepare_training_data()

    lagged_features = ['Health_spending_lag1',
                       'Education_spending_lag1', 'Military Spending_lag1']
    model_data = df.dropna(
        subset=['GDP_per_capita'] + lagged_features + ['previous_year'])

    country_dummies = pd.get_dummies(model_data['Country'], prefix='Country')
    gdp_country_features = list(country_dummies.columns)
    model_data = pd.concat([model_data, country_dummies], axis=1)
    model_data = model_data.drop(columns=['Country'])

    model_data, gdp_feature_means, gdp_feature_stds = normalize_features(
        model_data, fit=True)

    columns_to_use = lagged_features + ['previous_year'] + gdp_country_features
    X = model_data[columns_to_use].astype(np.float64).values
    X = np.column_stack([np.ones(len(X)), X])
    y = model_data['GDP_per_capita'].astype(np.float64).values

    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)
    y = np.nan_to_num(y, nan=0.0, posinf=1e6, neginf=-1e6)

    gdp_model_coefficients = regress(X, y)

    y_pred = np.dot(X, gdp_model_coefficients)
    r2 = r2_score(y, y_pred)

    print(f"GDP model trained with R² score: {r2:.4f}")
    print(f"Log-transformed features: {gdp_log_transformed_features}")
    return r2


train_gdp_model()


def predict_gdp(user_features, country, current_year=2024,
                coefficients=gdp_model_coefficients):
    """
    API prediction function for GDP per capita

    Args:
        user_features: [health_spending_pct, education_spending_pct, military_spending_pct] 
                      - Spending as % of GDP (interpreted as % of previous year's GDP)
        country: Country name (string, must be in trained countries)
        current_year: Current year (int, default 2024)
        coefficients: Pre-trained model coefficients

    Returns:
        float: Predicted GDP per capita for NEXT year (current_year + 1)
    """

    if coefficients is None:
        raise ValueError(
            "Model coefficients not available. Train model first.")

    if country not in country_code_to_name.values():
        raise ValueError(
            f"Country must be one of: {list(country_code_to_name.values())}")

    health_spending_pct, education_spending_pct, military_spending_pct = user_features

    feature_data = {
        'Health_spending_lag1': health_spending_pct,
        'Education_spending_lag1': education_spending_pct,
        'Military Spending_lag1': military_spending_pct,
        'previous_year': current_year
    }

    for country_feature in gdp_country_features:
        country_name = country_feature.replace('Country_', '')
        feature_data[country_feature] = 1 if country_name == country else 0

    feature_df = pd.DataFrame([feature_data])

    feature_df = normalize_features(
        feature_df,
        feature_means=gdp_feature_means,
        feature_stds=gdp_feature_stds,
        log_features=gdp_log_transformed_features,
        fit=False
    )

    lagged_features = ['Health_spending_lag1',
                       'Education_spending_lag1', 'Military Spending_lag1']
    columns_to_use = lagged_features + ['previous_year'] + gdp_country_features
    X = feature_df[columns_to_use].astype(np.float64).values

    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

    if coefficients.shape[0] == X.shape[1] + 1:
        X = np.hstack([np.ones((X.shape[0], 1)), X])

    prediction_normalized = np.dot(X, coefficients)[0]

    gdp_mean = gdp_feature_means.get('GDP_per_capita', 0)
    gdp_std = gdp_feature_stds.get('GDP_per_capita', 1)

    if gdp_std != 0:
        prediction_denormalized = (prediction_normalized * gdp_std) + gdp_mean
    else:
        prediction_denormalized = prediction_normalized

    if 'GDP_per_capita' in gdp_log_transformed_features:
        prediction_final = np.expm1(prediction_denormalized)
    else:
        prediction_final = prediction_denormalized

    return prediction_final


if __name__ == "__main__":
    try:
        predicted_gdp = predict_gdp(

            user_features=[10.9, 3.6, 1.0],
            country="Japan",
            current_year=2024
        )

        print(f"Predicted NEXT YEAR GDP per capita: ${predicted_gdp:,.2f}")

    except Exception as e:
        print(f"Prediction error: {e}")
