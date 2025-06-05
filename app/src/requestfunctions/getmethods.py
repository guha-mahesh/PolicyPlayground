import requests


def getPoliticians(user_id):
    return requests.get(f'http://web-api:4000/politician/fetchall/{user_id}')

def getPoliticianID(polName):
    return requests.get(f'http://web-api:4000/politicians/getID/{polName}')

def postNote(json1):
    requests.post("http://web-api:4000/notes/addnote", json=json1)

def getNotes(user_id, politician_id):
    return requests.get(f'http://web-api:4000/notes/getNotes/{user_id}/{politician_id}')

def getUserName(user_id):
    return requests.get(f'http://web-api:4000/users/getUser/{user_id}')

def savePolitician(returnJson):
    requests.post("http://web-api:4000/politician/newPolitician", json=returnJson)

def modifyNotes(json1):
    return requests.put("http://web-api:4000/notes/modifyNotes", json=json1)