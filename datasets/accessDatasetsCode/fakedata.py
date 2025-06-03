import random
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.metrics import classification_report


scopes = [
    'Neighborhood', 'City', 'County', 'State', 'Province',
    'Region', 'National', 'Cross-Border', 'Continental', 'International', 'Global'
]

durations = ['Temporary', 'Short-Term',
             'Medium-Term', 'Long-Term', 'Permanent', 'Trial']

intensities = [
    'Not Enforced', 'Symbolic Only', 'Minimal', 'Light Enforcement', 'Moderate Enforcement',
    'Strict Enforcement', 'Punitive', 'Community-Enforced', 'Surveillance-Based'
]

advocacy_methods = [
    'Petition', 'Protest', 'Op-ed', 'Media Outreach', 'Social Media Campaign',
    'Direct Email to Representative', 'Public Comment', 'Town Hall',
    'Join Advocacy Group', 'GoFundMe Awareness', 'Public Art', 'Citizen Report',
    'Lawsuit', 'Influencer Collaboration', 'Viral Video', 'Documentary',
    'Academic Paper', 'Meme Campaign', 'Podcast', 'Newsletter', 'Public Poll'
]


data = []
num_samples = 500

for _ in range(num_samples):
    scope = random.choice(scopes)
    duration = random.choice(durations)
    intensity = random.choice(intensities)

    if intensity in ['Strict Enforcement', 'Punitive'] and scope in ['National', 'International']:
        method = random.choice(
            ['Lobby Group', 'Media Outreach', 'Influencer Collaboration', 'Documentary'])
    elif scope in ['Neighborhood', 'City'] and duration in ['Temporary', 'Trial']:
        method = random.choice(['Town Hall', 'Petition', 'Public Comment'])
    elif intensity in ['Minimal', 'Symbolic Only']:
        method = random.choice(
            ['Social Media Campaign', 'Op-ed', 'Podcast', 'Meme Campaign'])
    else:
        method = random.choice(advocacy_methods)

    data.append({
        'Policy Scope': scope,
        'Policy Duration': duration,
        'Enforcement Intensity': intensity,
        'Best Advocacy Method': method
    })


df = pd.DataFrame(data)


print(df)

X = df[['Policy Scope', 'Policy Duration', 'Enforcement Intensity']]
y = df['Best Advocacy Method']

feature_encoder = OrdinalEncoder()
X_encoded = feature_encoder.fit_transform(X)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y_encoded, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

print(y_pred, "\n\n\n", y_test)
right = 0
for i in range(len(y_pred)):

    if y_pred[i] == y_test[i]:
        right += 1

print(right)
