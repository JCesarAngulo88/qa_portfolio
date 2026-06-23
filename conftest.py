
import pytest
import logging
import os

# Create a logger instance for this module
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def setup_logger():
    """
    Configures the root logger for the entire test run.
    """
    log_file_path = os.path.join(os.path.dirname(__file__), "app_test.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logger.info("Logger has been configured.")

@pytest.fixture
def base_url():
    """Returns the URL of the running Flask server."""
    logger.info("Setting Base URL")
    return os.getenv("BASE_URL", "http://127.0.0.1:5000")

# --- API Fixtures
from typing import Any, Generator
from tests.api.api_utils.api_client import APIClient
from tests.api.config.api_settings import Config

@pytest.fixture(scope="session")
def api_client() -> Generator[APIClient, None, None]:
    """Fixture to provide API client for all tests"""
    logger.info("Setting API Client")
    client = APIClient()
    yield client
    # Cleanup if needed
    client.session.close()

@pytest.fixture(scope="function")
def authenticated_client(api_client):
    """
    Fixture to provide an authenticated API client for a specific test.
    It calls the login() method defined to attach the JWT token to the session headers.
    """
    logger.info("Setting Authenticated Client")
    email = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    # Fail fast if credentials are missing
    if not email or not password:
        pytest.fail("API_USERNAME/API_PASSWORD or USERNAME/PASSWORD must be set in the environment")

    api_client.login(email=email, password=password)
    return api_client

@pytest.fixture(scope="function")
def test_user_data() -> dict[str, Any]:
    """Fixture to provide test user data"""
    logger.info("Setting Test User Data")
    return {
        "name": "Test User",
        "email": "test.user@example.com",
        "password": "TestPass123!",
        "role": "user"
    }

@pytest.fixture(scope="function")
def cleanup_test_user(api_client: APIClient):
    """Fixture to clean up test users after tests"""
    logger.info("Setting Clean Up")
    
    user_ids = []
    yield user_ids

    # Cleanup created users
    for user_id in user_ids:
        try:
            api_client.delete(f"/users/{user_id}")
            logger.info(f"Cleaned up test user: {user_id}")
        except:
            logger.warning(f"Failed to cleanup user: {user_id}")
