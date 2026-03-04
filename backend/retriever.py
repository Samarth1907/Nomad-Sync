import requests
import os

MAPS_KEY = os.getenv("AZURE_MAPS_KEY")

async def enrich_plan(plan):
    url = "https://atlas.microsoft.com/search/poi/json"

    params = {
        "subscription-key": MAPS_KEY,
        "query": "tourist attractions Mahabalipuram",
        "limit": 5,
        "api-version": "1.0"
    }

    r = requests.get(url, params=params)
    if r.status_code == 200:
        places = r.json().get("results", [])
    else:
        places = []

    return {
        "plan": plan,
        "places": places
    }
