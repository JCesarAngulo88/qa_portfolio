import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
    TIMEOUT = int(os.getenv("API_TIMEOUT", "5"))

    # Headers
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Test API timming settings
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", 30))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
