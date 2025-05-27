import requests
import json
import pandas as pd

url = "https://api.congress.gov/v3/member?currentMember=true&format=json&limit=250&api_key=HSPYhDCuoo1naxdRHWRwSBD8yPx1yuhbP2lz1NY8"

# Make the request
response = requests.get(url)

# Check if request was successful
if response.status_code == 200:
    # Parse JSON from response text
    data = response.json()  # This is the easiest way
    # OR alternatively: data = json.loads(response.text)

    print("API Response successful!")
    print(f"Total members found: {data['pagination']['count']}")

    # Extract the members data
    members = data['members']

    # Create a list to store member info
    member_list = []

    for member in members:
        member_info = {
            'name': member.get('name', 'N/A'),
            'bioguideId': member.get('bioguideId', 'N/A'),
            'state': member.get('state', 'N/A'),
            'party': member.get('partyName', 'N/A'),
            'district': member.get('district', 'N/A'),
            'url': member.get('url', 'N/A')
        }
        member_list.append(member_info)

    # Convert to DataFrame
    df = pd.DataFrame(member_list)

    api_string = "&api_key=HSPYhDCuoo1naxdRHWRwSBD8yPx1yuhbP2lz1NY8"

    new_urls = []
    urls = df['url'].tolist()
    for url in urls:
        new_url = url+api_string
        print(new_url)
        new_urls.append(new_url)

    df['new_urls'] = pd.Series(new_urls)
    print(new_urls)
    print(df['new_urls'])
else:
    print(f"Error: {response.status_code}")
    print(f"Response: {response.text}")
