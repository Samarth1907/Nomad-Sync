import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

async def plan_trip(data):
    prompt = f"""
    Create a structured travel itinerary plan.

    destination: {data['destination']}
    days: {data['days']}
    budget: {data['budget']}
    group size: {data['people']}

    return JSON with locations and schedule.
    """

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return resp.choices[0].message.content
