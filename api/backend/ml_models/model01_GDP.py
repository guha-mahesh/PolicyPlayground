import pandas as pd
import numpy as np
import requests


feature_means = {}
feature_stds = {}
country_features = []
log_transformed_features = set()


def train_func():

    global feature_means, feature_stds, country_features, log_transformed_features

    def create_gdp_lag(df, gdp_col='GDP_per_capita', lag_years=1):
        df = df.copy()

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
        dot1_reg = dot1
        inv = np.linalg.inv(dot1_reg)
        dot2 = np.dot(X.T, y)
        return np.dot(inv, dot2)

    def normalize_features(df, fit=True):
        df = df.copy()
        means = {}
        stds = {}
        log_features = set()

        for col in df.columns:
            if col == "mos" or col.startswith('Country_'):
                continue

            values = df[col].astype(np.float64)

            if (values >= 0).all() and values.max() > 1000:
                values = np.log1p(values)
                log_features.add(col)

            mean_val = values.mean()
            std_val = values.std()
            means[col] = mean_val
            stds[col] = std_val

            if std_val != 0:
                df[col] = (values - mean_val) / std_val
            else:
                df[col] = 0

        return df, means, stds, log_features

    def prepare_training_data():
        govt_health = requests.get(
            "http://web-api:4000/model/fetchData2/HealthExpenditure").json()['data']
        govt_education = requests.get(
            "http://web-api:4000/model/fetchData2/EducationExpenditure").json()['data']
        military_spending = requests.get(
            "http://web-api:4000/model/fetchData2/MilitaryExpenditure").json()['data']
        gdp_per_capita = requests.get(
            "http://web-api:4000/model/fetchData2/GDP").json()['data']

        df = pd.DataFrame(gdp_per_capita)
        health_df = pd.DataFrame(govt_health)
        education_df = pd.DataFrame(govt_education)
        military_df = pd.DataFrame(military_spending)

        print("Original GDP columns:", df.columns.tolist())
        print("Original Health columns:", health_df.columns.tolist())
        print("Original Education columns:", education_df.columns.tolist())
        print("Original Military columns:", military_df.columns.tolist())

        df = df.rename(columns={
            'country': 'Country',
            'mos': 'date',
            'vals': 'GDP_per_capita'
        })

        health_df = health_df.rename(columns={
            'country': 'Country',
            'mos': 'date',
            'vals': 'Health_spending'
        })

        education_df = education_df.rename(columns={
            'country': 'Country',
            'mos': 'date',
            'vals': 'Education_spending'
        })

        military_df = military_df.rename(columns={
            'country': 'Country',
            'mos': 'date',
            'vals': 'Military Spending'
        })

        print("\nRenamed GDP columns:", df.columns.tolist())
        print("Renamed Health columns:", health_df.columns.tolist())
        print("Renamed Education columns:", education_df.columns.tolist())
        print("Renamed Military columns:", military_df.columns.tolist())

        print("\nFirst 3 rows of GDP df:")
        print(df.head(3))
        print("\nFirst 3 rows of Health df:")
        print(health_df.head(3))

        df['GDP_per_capita'] = pd.to_numeric(
            df['GDP_per_capita'], errors='coerce')
        health_df['Health_spending'] = pd.to_numeric(
            health_df['Health_spending'], errors='coerce')
        education_df['Education_spending'] = pd.to_numeric(
            education_df['Education_spending'], errors='coerce')
        military_df['Military Spending'] = pd.to_numeric(
            military_df['Military Spending'], errors='coerce')

        try:
            df = df.merge(health_df, on=['Country', 'date'], how='outer')
        except KeyError as e:
            print(f"Merge failed with KeyError: {e}")
            print("GDP DataFrame info:")
            print(df.info())
            print("\nHealth DataFrame info:")
            print(health_df.info())
            raise

        df = df.merge(education_df, on=['Country', 'date'], how='outer')
        df = df.merge(military_df, on=['Country', 'date'], how='inner')

        df = create_gdp_lag(df, gdp_col='GDP_per_capita', lag_years=1)
        df['date'] = pd.to_numeric(df['date'])
        df['previous_year'] = df['date'] - 1

        return df

    df = prepare_training_data()

    lagged_features = ['Health_spending_lag1',
                       'Education_spending_lag1', 'Military Spending_lag1']
    model_data = df.dropna(
        subset=['GDP_per_capita'] + lagged_features + ['previous_year'])

    country_dummies = pd.get_dummies(model_data['Country'], prefix='Country')
    country_features = list(country_dummies.columns)
    model_data = pd.concat([model_data, country_dummies], axis=1)
    model_data = model_data.drop(columns=['Country'])

    model_data, feature_means, feature_stds, log_transformed_features = normalize_features(
        model_data, fit=True)

    columns_to_use = lagged_features + ['previous_year'] + country_features
    X = model_data[columns_to_use].astype(np.float64).values
    X = np.column_stack([np.ones(len(X)), X])
    y = model_data['GDP_per_capita'].astype(np.float64).values

    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)
    y = np.nan_to_num(y, nan=0.0, posinf=1e6, neginf=-1e6)

    coefficients = regress(X, y)
    api_base_url = "http://web-api:4000/model"

    gdp_payload = {
        "model_name": "GDP",
        "coefficients": coefficients.tolist()
    }
    response = requests.post(
        f"{api_base_url}/storeWeights", json=gdp_payload)
    if response.status_code != 200:
        print(f"Failed to store S&P 500 weights: {response.text}")


def predict(user_features, country, current_year=2024, coefficients=None):

    country_code_to_name = {
        "USA": "USA",
        "JPN": "JPN",
        "DEU": "DEU",
        "GBR": "GBR",
        "FRA": "FRA",
        "RUS": "RUS",
        "CAN": "CAN"
    }
    if coefficients is None:
        response = requests.get("http://web-api:4000/model/getWeights/GDP")
        if response.status_code == 200:
            coefficients = np.array(response.json()['coefficients'])

    def normalize_features(df, feature_means, feature_stds, log_features):
        df = df.copy()

        for col in df.columns:
            if col == "date" or col.startswith('Country_'):
                continue

            values = df[col].astype(np.float64)

            if col in log_features:
                values = np.log1p(values)

            mean_val = feature_means.get(col, 0)
            std_val = feature_stds.get(col, 1)

            if std_val != 0:
                df[col] = (values - mean_val) / std_val
            else:
                df[col] = 0

        return df

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

    for country_feature in country_features:
        country_name = country_feature.replace('Country_', '')
        feature_data[country_feature] = 1 if country_name == country else 0

    feature_df = pd.DataFrame([feature_data])

    feature_df = normalize_features(
        feature_df,
        feature_means=feature_means,
        feature_stds=feature_stds,
        log_features=log_transformed_features
    )

    lagged_features = ['Health_spending_lag1',
                       'Education_spending_lag1', 'Military Spending_lag1']
    columns_to_use = lagged_features + ['previous_year'] + country_features
    X = feature_df[columns_to_use].astype(np.float64).values

    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

    if coefficients.shape[0] == X.shape[1] + 1:
        X = np.hstack([np.ones((X.shape[0], 1)), X])

    prediction_normalized = np.dot(X, coefficients)[0]

    gdp_mean = feature_means.get('GDP_per_capita', 0)
    gdp_std = feature_stds.get('GDP_per_capita', 1)

    if gdp_std != 0:
        prediction_denormalized = (prediction_normalized * gdp_std) + gdp_mean
    else:
        prediction_denormalized = prediction_normalized

    if 'GDP_per_capita' in log_transformed_features:
        prediction_final = np.expm1(prediction_denormalized)
    else:
        prediction_final = prediction_denormalized

    return prediction_final
