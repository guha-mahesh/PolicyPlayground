import requests

def getPoliticians():
    return ['Guha', 'John Pork']

def getPoliticianID(polName):
    # requests.get("http://web-api:4000/politicians/getID/"+polName)
    return 1

def postNote(json1):
    requests.post("http://web-api:4000/notes/addnote", json=json1)

