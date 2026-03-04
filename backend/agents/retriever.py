"""
Retriever Agent — Uses Azure Maps API to fetch real POIs near planned
locations and optimize the route between activities.

In demo mode, returns curated POI data for Chennai/Mahabalipuram.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from models import TripPlan, Activity
import config

logger = logging.getLogger("nomad_sync.retriever")

AZURE_MAPS_BASE = "https://atlas.microsoft.com"


# ── Demo Enrichment ──────────────────────────────────────────────────

def _demo_enrich(plan: TripPlan) -> TripPlan:
    """Add realistic demo data for travel times and route info."""
    for day in plan.days:
        for i, act in enumerate(day.activities):
            if not act.travel_time_to_next and i < len(day.activities) - 1:
                act.travel_time_to_next = "15 min"
    return plan


# ── Azure Maps POI Search ────────────────────────────────────────────

async def _search_nearby_pois(
    lat: float, lon: float, query: str, limit: int = 5
) -> list[dict]:
    """Search for POIs near a coordinate using Azure Maps."""
    url = f"{AZURE_MAPS_BASE}/search/poi/json"
    params = {
        "subscription-key": config.AZURE_MAPS_KEY,
        "api-version": "1.0",
        "query": query,
        "lat": lat,
        "lon": lon,
        "radius": 5000,  # 5km radius
        "limit": limit,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            return resp.json().get("results", [])
        else:
            logger.warning(f"Azure Maps search failed: {resp.status_code}")
            return []


async def _get_route_summary(
    waypoints: list[tuple[float, float]],
) -> dict[str, Any]:
    """
    Get route summary (distance + travel time) between ordered waypoints
    using Azure Maps Route Directions API.
    """
    if len(waypoints) < 2:
        return {"total_distance_km": 0, "total_time_min": 0, "legs": []}

    # Build colon-separated coordinate pairs
    coords = ":".join(f"{lat},{lon}" for lat, lon in waypoints)
    url = f"{AZURE_MAPS_BASE}/route/directions/json"
    params = {
        "subscription-key": config.AZURE_MAPS_KEY,
        "api-version": "1.0",
        "query": coords,
        "travelMode": "car",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            logger.warning(f"Azure Maps route failed: {resp.status_code}")
            return {"total_distance_km": 0, "total_time_min": 0, "legs": []}

        data = resp.json()
        routes = data.get("routes", [])
        if not routes:
            return {"total_distance_km": 0, "total_time_min": 0, "legs": []}

        route = routes[0]
        summary = route.get("summary", {})
        legs = route.get("legs", [])

        leg_summaries = []
        for leg in legs:
            ls = leg.get("summary", {})
            leg_summaries.append({
                "distance_km": round(ls.get("lengthInMeters", 0) / 1000, 1),
                "time_min": round(ls.get("travelTimeInSeconds", 0) / 60),
            })

        return {
            "total_distance_km": round(
                summary.get("lengthInMeters", 0) / 1000, 1
            ),
            "total_time_min": round(
                summary.get("travelTimeInSeconds", 0) / 60
            ),
            "legs": leg_summaries,
        }


# ── Main Retriever Logic ─────────────────────────────────────────────

async def run_retriever_agent(plan: TripPlan) -> TripPlan:
    """
    Enrich the Planner's itinerary with real Azure Maps data:
    1. Validate/update coordinates for each activity via POI search
    2. Calculate actual travel times between activities via Route API
    """
    if config.DEMO_MODE:
        logger.info("Retriever running in DEMO mode")
        return _demo_enrich(plan)

    logger.info("Retriever running with Azure Maps API")

    try:
        for day in plan.days:
            # ── Step 1: Enrich each activity with real POI data ──
            for act in day.activities:
                if act.latitude and act.longitude:
                    pois = await _search_nearby_pois(
                        act.latitude, act.longitude, act.name, limit=1
                    )
                    if pois:
                        poi = pois[0]
                        pos = poi.get("position", {})
                        act.latitude = pos.get("lat", act.latitude)
                        act.longitude = pos.get("lon", act.longitude)
                        poi_info = poi.get("poi", {})
                        if poi_info.get("name"):
                            act.location = (
                                f"{poi_info['name']}, "
                                f"{poi.get('address', {}).get('freeformAddress', act.location)}"
                            )

            # ── Step 2: Calculate travel times between activities ──
            waypoints = [
                (act.latitude, act.longitude)
                for act in day.activities
                if act.latitude and act.longitude
            ]

            if len(waypoints) >= 2:
                route_info = await _get_route_summary(waypoints)
                legs = route_info.get("legs", [])
                for i, leg in enumerate(legs):
                    if i < len(day.activities):
                        day.activities[i].travel_time_to_next = (
                            f"{leg['time_min']} min"
                        )

        return plan

    except Exception as e:
        logger.error(f"Retriever agent error: {e}. Returning plan as-is.")
        return _demo_enrich(plan)
