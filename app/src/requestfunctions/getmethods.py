import requests


def getPoliticians(user_id):
    return requests.get(f'http://web-api:4000/politician/politicians/{user_id}')

def getPoliticianID(polName):
    return requests.get(f'http://web-api:4000/politician/politicianID/{polName}')

def postNote(json1):
    requests.post("http://web-api:4000/notes/note", json=json1)

def getNotes(user_id, politician_id):
    return requests.get(f'http://web-api:4000/notes/notes/{user_id}/{politician_id}')

def getUserName(user_id):
    return requests.get(f'http://web-api:4000/users/getUser/{user_id}')

def savePolitician(returnJson):
    requests.post("http://web-api:4000/politician/newPolitician", json=returnJson)

def savePolicy(json1):
    return requests.post("http://web-api:4000/politician/savePolicy", json=json1)

def getPolicy(saved_id):
    return requests.get(f'http://web-api:4000/politician/policy/{saved_id}')

def noteSavedPolicy(conversation_id):
    return requests.get(f'http://web-api:4000/notes/policy/{conversation_id}')

def modifyPolicy(json1):
    return requests.put("http://web-api:4000/politician/modifyPolicy", json=json1)

def modifyNotes(json1):
    return requests.put("http://web-api:4000/notes/modifyNotes", json=json1)

def predictSP(discount_rate, fed_balance, treasury_holdings):
    requests.get(f"http://web-api:4000/model/predictSp/{discount_rate},{fed_balance},{treasury_holdings}")

def predictGDP(military_spending, education_spending, health_spending, country):
    country_codes = {
        "United States": "USA",
        "Japan": "JPN",
        "Germany": "DEU",
        "United Kingdom": "GBR",
        "France": "FRA",
        "Russia": "RUS",
        "Canada": "CAN"
        }
    requests.get(f"http://host.docker.internal:4000/model/predictGDP/{military_spending},{education_spending},{health_spending}/{country_codes[country]}")

def PolicyFromConvoID(conversation_id):
    requests.get(f'http://web-api:4000/notes/policy/{conversation_id}')