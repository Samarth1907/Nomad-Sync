"""
Executor Agent — Generates deliverable files from the finalized trip plan:
  1. PDF Itinerary (styled, day-by-day plan using ReportLab)
  2. ICS Calendar File (importable events using icalendar)
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timedelta

from icalendar import Calendar, Event
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

from models import TripPlan
import config

logger = logging.getLogger("nomad_sync.executor")

# ── Color Palette ─────────────────────────────────────────────────────
BRAND_BLUE = colors.HexColor("#1a73e8")
BRAND_DARK = colors.HexColor("#202124")
BRAND_GRAY = colors.HexColor("#5f6368")
BRAND_LIGHT = colors.HexColor("#f8f9fa")
BRAND_ACCENT = colors.HexColor("#34a853")


# ── PDF Generation ────────────────────────────────────────────────────

def _generate_pdf(plan: TripPlan, filepath: str) -> None:
    """Generate a styled PDF itinerary using ReportLab."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "NomadTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=BRAND_BLUE,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "NomadSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=BRAND_GRAY,
        spaceAfter=16,
    )
    day_header_style = ParagraphStyle(
        "DayHeader",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=BRAND_DARK,
        spaceBefore=16,
        spaceAfter=8,
    )
    activity_name_style = ParagraphStyle(
        "ActivityName",
        parent=styles["Normal"],
        fontSize=11,
        textColor=BRAND_BLUE,
        fontName="Helvetica-Bold",
    )
    normal_style = ParagraphStyle(
        "NomadNormal",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BRAND_DARK,
        leading=14,
    )
    cost_style = ParagraphStyle(
        "CostStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BRAND_ACCENT,
        fontName="Helvetica-Bold",
    )

    elements: list = []

    # ── Header ──
    elements.append(Paragraph("🧭 Nomad-Sync Trip Plan", title_style))
    elements.append(Paragraph(plan.title, subtitle_style))
    elements.append(
        Paragraph(
            f"{plan.origin} → {plan.destination} &nbsp;|&nbsp; "
            f"{plan.num_days} days &nbsp;|&nbsp; "
            f"{plan.num_travelers} travelers &nbsp;|&nbsp; "
            f"Budget: ₹{plan.budget:,}",
            subtitle_style,
        )
    )
    if plan.summary:
        elements.append(Paragraph(plan.summary, normal_style))
    elements.append(Spacer(1, 10))
    elements.append(
        HRFlowable(
            width="100%", thickness=1, color=BRAND_BLUE, spaceAfter=12
        )
    )

    # ── Day-by-Day ──
    for day in plan.days:
        elements.append(
            Paragraph(
                f"📅 Day {day.day_number}: {day.title}", day_header_style
            )
        )

        if day.accommodation:
            elements.append(
                Paragraph(f"🏨 Stay: {day.accommodation}", normal_style)
            )
            elements.append(Spacer(1, 6))

        # Activities table
        table_data = [["Time", "Activity", "Details", "Cost"]]
        for act in day.activities:
            table_data.append([
                Paragraph(act.time_slot or "—", normal_style),
                Paragraph(act.name, activity_name_style),
                Paragraph(
                    f"{act.description[:100]}{'...' if len(act.description) > 100 else ''}"
                    + (f"<br/><i>📍 {act.location}</i>" if act.location else "")
                    + (f"<br/>🚗 {act.travel_time_to_next} to next" if act.travel_time_to_next else ""),
                    normal_style,
                ),
                Paragraph(
                    f"₹{act.estimated_cost}" if act.estimated_cost else "Free",
                    cost_style,
                ),
            ])

        col_widths = [55, 80, 260, 55]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dadce0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        elements.append(table)
        elements.append(Spacer(1, 12))

    # ── Footer ──
    elements.append(
        HRFlowable(
            width="100%", thickness=1, color=BRAND_BLUE, spaceBefore=12
        )
    )
    elements.append(
        Paragraph(
            f"💰 Total Estimated Cost: ₹{plan.total_estimated_cost:,}",
            ParagraphStyle(
                "TotalCost",
                parent=styles["Normal"],
                fontSize=14,
                textColor=BRAND_ACCENT,
                fontName="Helvetica-Bold",
                spaceBefore=8,
            ),
        )
    )
    elements.append(Spacer(1, 6))
    elements.append(
        Paragraph(
            "Generated by Nomad-Sync • Collaborative Multi-Agent Travel Engine",
            ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=8,
                textColor=BRAND_GRAY,
                alignment=1,  # CENTER
            ),
        )
    )

    doc.build(elements)


# ── ICS Calendar Generation ──────────────────────────────────────────

def _generate_ics(plan: TripPlan, filepath: str) -> None:
    """Generate an ICS calendar file with events for each activity."""
    cal = Calendar()
    cal.add("prodid", "-//Nomad-Sync//Travel Engine//EN")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", plan.title)

    # Start from tomorrow as the trip start date
    trip_start = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    for day in plan.days:
        day_date = trip_start + timedelta(days=day.day_number - 1)

        for act in day.activities:
            event = Event()
            event.add("summary", act.name)
            event.add(
                "description",
                f"{act.description}\n\n"
                f"Category: {act.category}\n"
                f"Estimated Cost: ₹{act.estimated_cost}\n"
                f"Travel to next: {act.travel_time_to_next or 'N/A'}",
            )
            if act.location:
                event.add("location", act.location)

            # Parse time_slot e.g. "09:00 - 11:00"
            if act.time_slot and "-" in act.time_slot:
                try:
                    parts = act.time_slot.split("-")
                    start_h, start_m = map(int, parts[0].strip().split(":"))
                    end_h, end_m = map(int, parts[1].strip().split(":"))
                    event.add(
                        "dtstart",
                        day_date.replace(hour=start_h, minute=start_m),
                    )
                    event.add(
                        "dtend",
                        day_date.replace(hour=end_h, minute=end_m),
                    )
                except (ValueError, IndexError):
                    event.add("dtstart", day_date.replace(hour=9, minute=0))
                    event.add("dtend", day_date.replace(hour=10, minute=0))
            else:
                event.add("dtstart", day_date.replace(hour=9, minute=0))
                event.add("dtend", day_date.replace(hour=10, minute=0))

            event.add("uid", f"{uuid.uuid4()}@nomad-sync")
            cal.add_component(event)

    with open(filepath, "wb") as f:
        f.write(cal.to_ical())


# ── Main Executor Logic ──────────────────────────────────────────────

async def run_executor_agent(plan: TripPlan) -> dict[str, str]:
    """
    Generate PDF and ICS files from the finalized trip plan.
    Returns dict with trip_id, pdf_filename, and ics_filename.
    """
    trip_id = str(uuid.uuid4())[:8]
    pdf_filename = f"nomad_sync_{trip_id}.pdf"
    ics_filename = f"nomad_sync_{trip_id}.ics"
    pdf_path = os.path.join(config.OUTPUT_DIR, pdf_filename)
    ics_path = os.path.join(config.OUTPUT_DIR, ics_filename)

    logger.info(f"Executor generating files for trip {trip_id}")

    try:
        _generate_pdf(plan, pdf_path)
        logger.info(f"PDF generated: {pdf_path}")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        pdf_filename = ""

    try:
        _generate_ics(plan, ics_path)
        logger.info(f"ICS generated: {ics_path}")
    except Exception as e:
        logger.error(f"ICS generation failed: {e}")
        ics_filename = ""

    return {
        "trip_id": trip_id,
        "pdf_filename": pdf_filename,
        "ics_filename": ics_filename,
    }
