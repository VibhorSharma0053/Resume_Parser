# app/core/config.py

import os
from dotenv import load_dotenv

# Load the .env file so we can read its values
load_dotenv()

class Settings:
    """
    This class holds all the settings for our application.
    It reads values from the .env file.
    """

    # App general info
    APP_NAME: str = "Resume Parser API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Upload a resume and get structured JSON output"

    # Groq API settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3-8b-8192")

    # File upload settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx"]

    # Upload folder
    UPLOAD_DIR: str = "uploads"


# Create one single instance of Settings
# All other files will import this object
settings = Settings()