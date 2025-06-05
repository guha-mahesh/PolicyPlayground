import itertools
import random
import pandas as pd

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

# Generate every combination
combinations = list(itertools.product(scopes, durations, intensities))

data = []

for scope, duration, intensity in combinations:
    # Simplify intensity to "low, medium, high"
    if intensity in ['Not Enforced', 'Symbolic Only', 'Minimal']:
        intensity_level = 'low'
    elif intensity in ['Light Enforcement', 'Moderate Enforcement', 'Community-Enforced']:
        intensity_level = 'medium'
    else:
        intensity_level = 'high'

    # Determine if it's local, regional, national/global
    if scope in ['Neighborhood', 'City', 'County']:
        level = 'local'
    elif scope in ['State', 'Province', 'Region']:
        level = 'regional'
    else:
        level = 'global'

    # Determine if short/long-term
    if duration in ['Temporary', 'Trial', 'Short-Term']:
        term = 'short'
    elif duration in ['Long-Term', 'Permanent']:
        term = 'long'
    else:
        term = 'medium'

    if intensity_level == 'low':
        method = random.choice([
            'Social Media Campaign', 'Op-ed', 'Podcast', 'Meme Campaign', 'Public Poll'
        ])
    elif intensity_level == 'medium':
        if level == 'local':
            method = random.choice([
                'Town Hall', 'Petition', 'Public Comment', 'Direct Email to Representative'
            ])
        elif level == 'regional':
            method = random.choice([
                'Public Art', 'Public Poll', 'Join Advocacy Group', 'Citizen Report'
            ])
        else:  # global
            method = random.choice([
                'Media Outreach', 'Documentary', 'Influencer Collaboration', 'Newsletter'
            ])
    else:  # high intensity
        if level == 'local':
            method = random.choice([
                'Protest', 'Town Hall', 'Public Comment'
            ])
        elif level == 'regional':
            method = random.choice([
                'Lawsuit', 'Citizen Report', 'Direct Email to Representative'
            ])
        else:  # global
            method = random.choice([
                'Lawsuit', 'Media Outreach', 'Influencer Collaboration', 'Documentary'
            ])

    if term == 'long' and intensity_level == 'high' and level == 'global':
        method = random.choice([
            'Lawsuit', 'Academic Paper', 'Documentary'
        ])

    data.append({
        'Policy Scope': scope,
        'Policy Duration': duration,
        'Enforcement Intensity': intensity,
        'Best Advocacy Method': method
    })

df = pd.DataFrame(data)
print(df)
