import requests


def getPoliticians(user_id):
    return requests.get("http://web-api:4000/politician/fetchall/"+str(user_id))


def getPoliticianID(polName):
    return requests.get("http://web-api:4000/politicians/getID/"+polName)


def postNote(json1):
    requests.post("http://web-api:4000/notes/addnote", json=json1)


def getUserName(user_id):
    return requests.get("http://web-api:4000/users/getUser/" + str(user_id))
