"""
Orchestrator — Manages the sequential agent pipeline:
  Planner → Retriever → Executor

Provides progress tracking and error handling for each stage.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from models import TripRequest, TripPlan, TripResponse
from agents.planner import run_planner_agent
from agents.retriever import run_retriever_agent
from agents.executor import run_executor_agent
import config

logger = logging.getLogger("nomad_sync.orchestrator")


class TripPipeline:
    """
    Orchestrates the three-agent pipeline for trip planning.
    Tracks the current stage for progress reporting.
    """

    STAGES = ["planning", "retrieving", "executing", "completed"]

    def __init__(self) -> None:
        self.current_stage: str = "idle"
        self.progress_callback: Optional[Callable[[str, str], None]] = None

    def _update_stage(self, stage: str, detail: str = "") -> None:
        self.current_stage = stage
        if self.progress_callback:
            self.progress_callback(stage, detail)
        logger.info(f"Pipeline stage: {stage} — {detail}")

    async def run(self, req: TripRequest) -> TripResponse:
        """
        Run the full trip planning pipeline.

        Args:
            req: User's trip request parameters.

        Returns:
            TripResponse with the completed plan, PDF/ICS filenames, and metadata.
        """
        logger.info(
            f"Starting pipeline: {req.origin} → {req.destination}, "
            f"{req.num_days} days, ₹{req.budget}"
        )

        # ── Stage 1: Planner ──
        self._update_stage(
            "planning",
            f"Creating itinerary for {req.destination}..."
        )
        plan: TripPlan = await run_planner_agent(req)
        logger.info(
            f"Planner done: {len(plan.days)} days, "
            f"{sum(len(d.activities) for d in plan.days)} activities"
        )

        # ── Stage 2: Retriever ──
        self._update_stage(
            "retrieving",
            "Enriching with real POI data and optimizing routes..."
        )
        enriched_plan: TripPlan = await run_retriever_agent(plan)
        logger.info("Retriever done: plan enriched with map data")

        # ── Stage 3: Executor ──
        self._update_stage(
            "executing",
            "Generating PDF itinerary and calendar file..."
        )
        outputs: dict[str, str] = await run_executor_agent(enriched_plan)
        logger.info(f"Executor done: trip_id={outputs['trip_id']}")

        # ── Complete ──
        self._update_stage("completed", "Trip plan ready!")

        return TripResponse(
            trip_id=outputs["trip_id"],
            status="completed",
            demo_mode=config.DEMO_MODE,
            plan=enriched_plan,
            pdf_filename=outputs.get("pdf_filename"),
            ics_filename=outputs.get("ics_filename"),
        )
