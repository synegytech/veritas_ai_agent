# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Define the base directory of the project
# This assumes config.py is in the root directory. Adjust if needed.
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Loads settings from environment variables and .env file."""

    google_ai_api_key: str
    veritas_ai_model: str = (
        "gemini-1.5-flash"  # Default model "gemini-2.0-pro-exp-02-05"
    )
    veritas_data_file_path: str = "veritas_data/Veritas_data.pdf"  # Default path

    # Construct the absolute path for the data file
    @property
    def absolute_veritas_data_path(self) -> Path:
        # Assumes the path in .env is relative to the project root
        return BASE_DIR / self.veritas_data_file_path

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",  # Load .env file from the base directory
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields in .env
    )


# Create a single instance of settings to be imported elsewhere
settings = Settings()

# --- Configure Logging ---
# You can configure logging here more robustly if needed
# For simplicity, we'll rely on FastAPI/Uvicorn's default logging for now,
# but you might want to set up file logging, formatting, etc. here later.
import logging

logging.basicConfig(level=logging.INFO)  # Basic config
logger = logging.getLogger(__name__)

# Validate that the data file exists on startup
if not settings.absolute_veritas_data_path.exists():
    logger.error(
        f"CRITICAL: Veritas data file not found at configured path: {settings.absolute_veritas_data_path}"
    )
    # You might want to raise an exception here to prevent the app from starting
    # raise FileNotFoundError(f"Veritas data file not found: {settings.absolute_veritas_data_path}")
else:
    logger.info(f"Veritas data file found at: {settings.absolute_veritas_data_path}")
