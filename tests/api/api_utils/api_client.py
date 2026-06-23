import requests
import logging
from typing import Optional, Dict, Any
from tests.api.config.api_settings import Config
from tests.api.config.api_endpoints import EndPoints

logger = logging.getLogger(__name__)

class APIClient:
    """Wrapper for API requests with built-in authentication and retry logic"""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or Config.BASE_URL
        self.session = requests.Session()
        self.token = None
        self.session.headers.update(Config.DEFAULT_HEADERS)

    def login(self, email, password):
        """
        Performs authentication against the /login endpoint.
        If successful, it updates the session headers with the JWT token.
        """
        url = f"{self.base_url}{EndPoints.LOGIN}"
        payload = {"username": email, "password": password}

        logger.info(f"Initiating login request to {url} for user: {email}")

        try:
            response = self.session.post(url, headers=self.session.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token") or data.get("token")
                logger.info(f"\nToken Created: {self.token}\n")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                logger.info(f"Header with Token: {self.session.headers}")

                logger.info("Login successful.")
                return response

            logger.error(f"Login failed. Status: {response.status_code}, Msg: {response.text}")
            return response

        except Exception as e:
            logger.error(f"Error during login process: {str(e)}")
            raise

    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.token = token

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"

        # Add timeout if not specified
        if 'timeout' not in kwargs:
            kwargs['timeout'] = Config.TEST_TIMEOUT

        logger.debug(f"Making {method} request to {url}")

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    # HTTP method shortcuts
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs):
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs):
        raise_error = kwargs.pop('raise_error', True)

        url = f"{self.base_url}{endpoint}"
        print(f"Making POST request to {url}")

        response = self.session.post(url, json=json, **kwargs)

        if raise_error:
            response.raise_for_status()

        return response

    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs):
        return self._request("PUT", endpoint, data=data, json=json, **kwargs)

    def patch(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs):
        return self._request("PATCH", endpoint, data=data, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)
