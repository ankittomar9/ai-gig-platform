import pytest
import tempfile
from pathlib import Path
import app.config
import app.database
from app.database import init_db, save_or_update_jobs, set_setting, get_settings
from app.scrapers.direct_platforms import DIRECT_PLATFORM_POSTS

# Create isolated test database directory for the entire test session
_test_dir = tempfile.TemporaryDirectory()
_test_db_path = Path(_test_dir.name) / "test_gighunter.db"

# Redirect DB_PATH before any test module runs
app.config.DB_PATH = _test_db_path
app.database.DB_PATH = _test_db_path

# Initialize schema and seed direct platform jobs
init_db()
save_or_update_jobs(DIRECT_PLATFORM_POSTS)

@pytest.fixture(autouse=True, scope="function")
def isolate_and_cleanup_test_settings():
    """Ensure tests run against isolated DB and reset mutated settings after each test"""
    # Ensure DB_PATH points to test DB
    app.config.DB_PATH = _test_db_path
    app.database.DB_PATH = _test_db_path
    
    yield
    
    # Restore clean settings in isolated test DB
    set_setting("offline_mode", "false")
    set_setting("gemini_api_key", "")
    set_setting("gemini_model", "gemini-3.8-flash")
