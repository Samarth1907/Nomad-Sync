"""
Nomad-Sync Configuration
Loads Azure credentials and app settings from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Azure OpenAI ──────────────────────────────────────────────────────
AZURE_OPENAI_KEY = ""
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_DEPLOYMENT = "gpt-4o"
AZURE_OPENAI_API_VERSION = "2024-06-01"

# ── Azure Maps ────────────────────────────────────────────────────────
AZURE_MAPS_KEY = ""

# ── App Settings ──────────────────────────────────────────────────────
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
DEMO_MODE = (
    not AZURE_OPENAI_KEY
    or not AZURE_OPENAI_ENDPOINT
    or not AZURE_MAPS_KEY
)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
