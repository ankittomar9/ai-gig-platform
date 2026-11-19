import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "gighunter.db"
STATIC_DIR = BASE_DIR / "app" / "static"

DEFAULT_SETTINGS = {
    "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
    "gemini_model": "gemini-2.5-flash",
    "offline_mode": False,
    "target_roles": ["AI Trainer", "RLHF Specialist", "Prompt Engineer", "Code Reviewer", "Domain Expert", "Data Annotator"],
    "minimum_rate": 0
}
