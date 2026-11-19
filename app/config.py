import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Load .env file if present
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

DB_PATH = DATA_DIR / "gighunter.db"
STATIC_DIR = BASE_DIR / "app" / "static"

DEFAULT_SETTINGS = {
    "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
    "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
    "offline_mode": os.getenv("OFFLINE_MODE", "false").lower() == "true",
    "target_roles": ["AI Trainer", "RLHF Specialist", "Prompt Engineer", "Code Reviewer", "Domain Expert", "Data Annotator"],
    "minimum_rate": 0
}
