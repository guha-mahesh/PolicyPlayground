import requests


def getPoliticians(user_id):
    return requests.get(f'http://web-api:4000/politician/politicians/{user_id}')

def savePolitician(returnJson):
    return requests.post("http://web-api:4000/politician/newPolitician", json=returnJson)



def getNotes(user_id, politician_id):
    return requests.get(f'http://web-api:4000/notes/notes/{user_id}/{politician_id}')

def postNote(json1):
    return requests.post("http://web-api:4000/notes/note", json=json1)

def modifyNotes(json1):
    return requests.put("http://web-api:4000/notes/note", json=json1)



def savePolicy(json1):
    return requests.post("http://web-api:4000/politician/policy", json=json1)

def modifyPolicy(json1):
    return requests.put("http://web-api:4000/politician/policy", json=json1)

def getPolicy(saved_id):
    return requests.get(f'http://web-api:4000/politician/policy/{saved_id}')

def noteSavedPolicy(conversation_id):
    return requests.get(f'http://web-api:4000/notes/policy/{conversation_id}')



def predictSP(discount_rate, fed_balance, treasury_holdings):
    return requests.get(f"http://web-api:4000/model/SP500/{discount_rate},{fed_balance},{treasury_holdings}")

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
    return requests.get(f"http://host.docker.internal:4000/model/GDP/{military_spending},{education_spending},{health_spending}/{country_codes[country]}")
