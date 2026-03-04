"""
Nomad-Sync Backend — FastAPI Application

Endpoints for trip planning, file downloads, and health checks.
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models import TripRequest, TripResponse, HealthResponse
from orchestrator import TripPipeline
import config

# ── Logging Setup ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)s │ %(levelname)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nomad_sync")

# ── FastAPI App ───────────────────────────────────────────────────────
app = FastAPI(
    title="Nomad-Sync API",
    description="Collaborative Multi-Agent Travel Engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory trip storage (prototype — replace with DB in production)
trip_store: dict[str, TripResponse] = {}

# Pipeline instance
pipeline = TripPipeline()


# ── Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        demo_mode=config.DEMO_MODE,
        version="0.1.0",
    )


@app.post("/api/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    """
    Run the full Planner → Retriever → Executor pipeline.
    Returns completed trip plan with PDF/ICS download info.
    """
    logger.info(
        f"New trip request: {request.origin} → {request.destination}"
    )

    try:
        response = await pipeline.run(request)
        # Store result for later retrieval
        trip_store[response.trip_id] = response
        return response
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Trip planning failed: {str(e)}",
        )


@app.get("/api/trip/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: str):
    """Retrieve a previously generated trip plan."""
    if trip_id not in trip_store:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip_store[trip_id]


@app.get("/api/download/{trip_id}/pdf")
async def download_pdf(trip_id: str):
    """Download the generated PDF itinerary."""
    if trip_id not in trip_store:
        raise HTTPException(status_code=404, detail="Trip not found")

    trip = trip_store[trip_id]
    if not trip.pdf_filename:
        raise HTTPException(status_code=404, detail="PDF not available")

    filepath = os.path.join(config.OUTPUT_DIR, trip.pdf_filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=trip.pdf_filename,
    )


@app.get("/api/download/{trip_id}/ics")
async def download_ics(trip_id: str):
    """Download the generated ICS calendar file."""
    if trip_id not in trip_store:
        raise HTTPException(status_code=404, detail="Trip not found")

    trip = trip_store[trip_id]
    if not trip.ics_filename:
        raise HTTPException(status_code=404, detail="ICS not available")

    filepath = os.path.join(config.OUTPUT_DIR, trip.ics_filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="ICS file not found")

    return FileResponse(
        filepath,
        media_type="text/calendar",
        filename=trip.ics_filename,
    )


# ── Startup Banner ───────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    mode = "🎭 DEMO MODE" if config.DEMO_MODE else "🚀 LIVE MODE"
    logger.info(f"╔══════════════════════════════════════╗")
    logger.info(f"║   🧭 Nomad-Sync API — {mode:10s}   ║")
    logger.info(f"╚══════════════════════════════════════╝")
    if config.DEMO_MODE:
        logger.info(
            "Running without Azure keys — using curated demo data."
        )
