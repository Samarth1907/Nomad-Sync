"""
Nomad-Sync Data Models
Pydantic schemas for request/response and internal pipeline data.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


# ── Request ───────────────────────────────────────────────────────────

class TripRequest(BaseModel):
    origin: str = Field(..., example="Chennai")
    destination: str = Field(..., example="Mahabalipuram")
    num_days: int = Field(2, ge=1, le=10)
    budget: int = Field(5000, ge=500)
    num_travelers: int = Field(1, ge=1, le=20)
    interests: list[str] = Field(
        default_factory=lambda: ["temples", "beaches"],
        example=["temples", "beaches", "food"],
    )


# ── Internal Pipeline Models ─────────────────────────────────────────

class Activity(BaseModel):
    name: str
    description: str = ""
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    time_slot: str = ""           # e.g. "09:00 - 11:00"
    estimated_cost: int = 0       # INR
    category: str = ""            # e.g. "sightseeing", "food"
    travel_time_to_next: str = "" # e.g. "25 min"


class ItineraryDay(BaseModel):
    day_number: int
    title: str = ""               # e.g. "Ancient Temples & Beach Vibes"
    activities: list[Activity] = []
    accommodation: str = ""


class TripPlan(BaseModel):
    title: str
    origin: str
    destination: str
    num_days: int
    num_travelers: int
    budget: int
    summary: str = ""
    days: list[ItineraryDay] = []
    total_estimated_cost: int = 0


# ── Response ──────────────────────────────────────────────────────────

class TripResponse(BaseModel):
    trip_id: str
    status: str = "completed"
    demo_mode: bool = False
    plan: TripPlan
    pdf_filename: Optional[str] = None
    ics_filename: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    demo_mode: bool = False
    version: str = "0.1.0"
