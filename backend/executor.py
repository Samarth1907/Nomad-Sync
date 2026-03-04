from fpdf import FPDF
import uuid
import os

OUTPUT_DIR = "outputs"

async def generate_outputs(data):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_id = str(uuid.uuid4())
    pdf_path = f"{OUTPUT_DIR}/{file_id}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0,10,"Nomad-Sync Trip Plan",ln=True)

    for place in data.get("places", []):
        pdf.cell(0,10,place["poi"]["name"],ln=True)

    pdf.output(pdf_path)

    return {
        "itinerary_pdf": pdf_path,
        "plan": data["plan"]
    }
