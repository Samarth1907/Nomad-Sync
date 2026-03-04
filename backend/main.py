from fastapi import FastAPI
from planner import plan_trip
from retriever import enrich_plan
from executor import generate_outputs

app = FastAPI()

@app.post("/plan_trip")
async def plan_trip_endpoint(data: dict):
    plan = await plan_trip(data)
    enriched = await enrich_plan(plan)
    result = await generate_outputs(enriched)
    return result
