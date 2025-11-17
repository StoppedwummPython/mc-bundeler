import requests

def get(url: str):
    return requests.get(url).json()