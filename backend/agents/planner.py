"""
Planner Agent — Uses AutoGen + Azure OpenAI GPT-4o to generate a structured
travel itinerary from the user's trip request.

In demo mode, returns a curated Chennai → Mahabalipuram itinerary.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from models import TripPlan, ItineraryDay, Activity, TripRequest
import config

logger = logging.getLogger("nomad_sync.planner")


# ── Demo Data ─────────────────────────────────────────────────────────

def _demo_plan(req: TripRequest) -> TripPlan:
    """Return a realistic hardcoded itinerary for demo purposes."""
    return TripPlan(
        title=f"Trip to {req.destination}",
        origin=req.origin,
        destination=req.destination,
        num_days=req.num_days,
        num_travelers=req.num_travelers,
        budget=req.budget,
        summary=(
            f"An exciting {req.num_days}-day trip from {req.origin} to "
            f"{req.destination} for {req.num_travelers} travelers, packed "
            f"with {', '.join(req.interests)}!"
        ),
        days=[
            ItineraryDay(
                day_number=1,
                title="Ancient Temples & Coastal Marvels",
                activities=[
                    Activity(
                        name="Shore Temple",
                        description="UNESCO World Heritage Site overlooking the Bay of Bengal. "
                                    "A stunning 8th-century granite temple complex.",
                        location="Shore Temple, Mahabalipuram",
                        latitude=12.6168,
                        longitude=80.1996,
                        time_slot="09:00 - 11:00",
                        estimated_cost=50,
                        category="sightseeing",
                    ),
                    Activity(
                        name="Pancha Rathas (Five Rathas)",
                        description="Monolithic rock-cut temples dating back to the 7th century. "
                                    "Each ratha is carved from a single granite boulder.",
                        location="Five Rathas, Mahabalipuram",
                        latitude=12.6107,
                        longitude=80.1938,
                        time_slot="11:30 - 13:00",
                        estimated_cost=50,
                        category="sightseeing",
                        travel_time_to_next="10 min",
                    ),
                    Activity(
                        name="Lunch at Moonrakers",
                        description="Seafood restaurant with stunning ocean views. "
                                    "Famous for its prawn curry and fish fry.",
                        location="Othavadai Street, Mahabalipuram",
                        latitude=12.6190,
                        longitude=80.1935,
                        time_slot="13:30 - 14:30",
                        estimated_cost=400,
                        category="food",
                        travel_time_to_next="5 min",
                    ),
                    Activity(
                        name="Arjuna's Penance",
                        description="World's largest open-air rock relief carving. "
                                    "A 27m × 9m marvel depicting scenes from the Mahabharata.",
                        location="Arjuna's Penance, Mahabalipuram",
                        latitude=12.6162,
                        longitude=80.1927,
                        time_slot="15:00 - 16:30",
                        estimated_cost=0,
                        category="sightseeing",
                        travel_time_to_next="15 min",
                    ),
                    Activity(
                        name="Mahabalipuram Beach Sunset",
                        description="Relax on the golden sands and watch the sunset "
                                    "over the Bay of Bengal. Street-food stalls nearby.",
                        location="Mahabalipuram Beach",
                        latitude=12.6198,
                        longitude=80.1953,
                        time_slot="17:00 - 18:30",
                        estimated_cost=100,
                        category="leisure",
                    ),
                ],
                accommodation="Hotel Mahabs, Mahabalipuram (₹1,200/night)",
            ),
            ItineraryDay(
                day_number=2,
                title="Hidden Gems & Return Journey",
                activities=[
                    Activity(
                        name="Tiger Cave",
                        description="Rock-cut temple with stunning tiger-head reliefs. "
                                    "Less crowded gem surrounded by casuarina groves.",
                        location="Tiger Cave, Saluvankuppam",
                        latitude=12.5845,
                        longitude=80.1937,
                        time_slot="08:00 - 09:30",
                        estimated_cost=0,
                        category="sightseeing",
                        travel_time_to_next="20 min",
                    ),
                    Activity(
                        name="Crocodile Bank",
                        description="One of the largest reptile zoos in Asia. Home to 2,400+ "
                                    "crocodiles, alligators, and turtles.",
                        location="Crocodile Bank, Vadanemmeli",
                        latitude=12.7443,
                        longitude=80.2344,
                        time_slot="10:00 - 12:00",
                        estimated_cost=50,
                        category="sightseeing",
                        travel_time_to_next="15 min",
                    ),
                    Activity(
                        name="Lunch at Bay's Restaurant",
                        description="Authentic South Indian meals (banana leaf thali) "
                                    "with fresh local fish preparations.",
                        location="East Coast Road, Mahabalipuram",
                        latitude=12.6160,
                        longitude=80.1940,
                        time_slot="12:30 - 13:30",
                        estimated_cost=350,
                        category="food",
                        travel_time_to_next="5 min",
                    ),
                    Activity(
                        name="Shopping – Stone Sculpture Market",
                        description="Browse hand-carved granite sculptures, souvenirs, "
                                    "and traditional crafts made by local artisans.",
                        location="Sculpture Market, Mahabalipuram",
                        latitude=12.6155,
                        longitude=80.1925,
                        time_slot="14:00 - 15:30",
                        estimated_cost=500,
                        category="shopping",
                        travel_time_to_next="10 min",
                    ),
                    Activity(
                        name="Return to Chennai",
                        description="Scenic drive back along East Coast Road (ECR). "
                                    "Approx 1.5 hours depending on traffic.",
                        location="ECR Highway",
                        latitude=12.8231,
                        longitude=80.2040,
                        time_slot="16:00 - 17:30",
                        estimated_cost=300,
                        category="transport",
                    ),
                ],
                accommodation="N/A (returning home)",
            ),
        ],
        total_estimated_cost=3000,
    )


# ── Live Planner (AutoGen + Azure OpenAI) ────────────────────────────

PLANNER_SYSTEM_PROMPT = """\
You are the Planner Agent of Nomad-Sync, a multi-agent travel planning system.

Given trip parameters, create a detailed, structured travel itinerary.
Output ONLY valid JSON matching this schema (no markdown, no explanation):

{
  "title": "Trip to <destination>",
  "origin": "<origin>",
  "destination": "<destination>",
  "num_days": <int>,
  "num_travelers": <int>,
  "budget": <int in INR>,
  "summary": "<1-2 sentence exciting summary>",
  "total_estimated_cost": <int in INR>,
  "days": [
    {
      "day_number": <int>,
      "title": "<catchy day title>",
      "accommodation": "<hotel name and price>",
      "activities": [
        {
          "name": "<place name>",
          "description": "<2-3 sentence vivid description>",
          "location": "<address or landmark>",
          "latitude": <float>,
          "longitude": <float>,
          "time_slot": "<HH:MM - HH:MM>",
          "estimated_cost": <int in INR per person>,
          "category": "<sightseeing|food|leisure|transport|shopping|adventure>",
          "travel_time_to_next": "<X min>"
        }
      ]
    }
  ]
}

Rules & Responsible AI Guardrails:
- MUST output ONLY valid JSON format. Do NOT wrap in markdown blocks like ```json.
- total_estimated_cost MUST stay within the provided budget. Do not hallucinate unrealistic low prices.
- Safety First: Do not include activities that are unsafe, illegal, or physically impossible for a general traveler.
- Respect local customs and regulations in the generated descriptions and activities.
- Include 4-6 activities per day, ensuring geographic efficiency (close-by places grouped together).
- Mix categories based on user interests.
- Provide realistic Indian pricing in INR.
- Include realistic travel time between consecutive activities.
"""


async def run_planner_agent(req: TripRequest) -> TripPlan:
    """
    Run the Planner Agent to generate a trip itinerary.
    Falls back to demo data when Azure keys are unavailable.
    """
    if config.DEMO_MODE:
        logger.info("Planner running in DEMO mode")
        return _demo_plan(req)

    logger.info("Planner running with Azure OpenAI GPT-4o")

    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

        model_client = AzureOpenAIChatCompletionClient(
            azure_deployment=config.AZURE_OPENAI_DEPLOYMENT,
            model=config.AZURE_OPENAI_DEPLOYMENT,
            api_key=config.AZURE_OPENAI_KEY,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_version=config.AZURE_OPENAI_API_VERSION,
        )

        agent = AssistantAgent(
            name="planner_agent",
            model_client=model_client,
            system_message=PLANNER_SYSTEM_PROMPT,
        )

        user_message = (
            f"Plan a trip:\n"
            f"- Origin: {req.origin}\n"
            f"- Destination: {req.destination}\n"
            f"- Days: {req.num_days}\n"
            f"- Budget: ₹{req.budget} (total for the group)\n"
            f"- Group size: {req.num_travelers}\n"
            f"- Interests: {', '.join(req.interests)}\n"
        )

        result = await agent.run(task=user_message)
        await model_client.close()

        # Extract the text response from the agent
        response_text = result.messages[-1].content
        # Clean potential markdown code fences
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        # Additional cleanup to ensure valid JSON if there is leading/trailing text
        response_text = response_text.strip()
        if response_text.startswith("`"):
            response_text = response_text.strip("`")
        
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            response_text = response_text[start_idx:end_idx+1]

        plan_data = json.loads(response_text)
        plan = TripPlan(**plan_data)
        return plan

    except Exception as e:
        logger.error(f"Planner agent error: {e}. Falling back to demo plan.")
        return _demo_plan(req)
