# pytest -v -s -m macaco tests/api/test_cases/test_auth.py

import logging
import pytest
import os

from tests.api.config.api_endpoints import EndPoints
from tests.api.config.api_settings import Config

logger = logging.getLogger(__name__)


class TestAuthEndpoints:

    @pytest.mark.debug
    @pytest.mark.cont_test
    def test_login_with_valid_credentials_returns_tokens(self, api_client):
        logger.info(
            f"Starting auth test: verify valid credentials return access and refresh tokens from {EndPoints.LOGIN}."
        )

        response = api_client.post(
            EndPoints.LOGIN,
            json={
                "username": os.getenv("USERNAME"),
                "password": os.getenv("PASSWORD")
            },
        )
        logger.info(f"Login response status: {response.status_code}")
        logger.info(f"Login response body: {response.json()}")

        assert response.status_code == 200
        logger.info("Assertion passed: login returns 200.")

        payload = response.json()
        assert payload["token_type"] == "Bearer"
        logger.info("Assertion passed: token_type is Bearer.")
        assert payload["expires_in"] > 0
        logger.info("Assertion passed: expires_in is positive.")
        assert isinstance(payload["access_token"], str)
        logger.info("Assertion passed: access_token is a string.")
        assert isinstance(payload["refresh_token"], str)
        logger.info("Assertion passed: refresh_token is a string.")

    @pytest.mark.debug
    @pytest.mark.cont_test
    @pytest.mark.parametrize(
        ("username", "password"),
        [
            ("admin", "wrong-password"),
            ("wrong-user", "password"),
            ("", "password"),
        ],
    )
    def test_login_with_invalid_credentials_returns_401(self, api_client, username, password):
        logger.info(f"Starting auth failure test: verify invalid credentials return 401 for username={username}.")

        response = api_client.post(
            EndPoints.LOGIN,
            json={"username": username, "password": password},
            raise_error=False,
        )

        logger.info(f"Login failure response status: {response.status_code}, body: {response.json()}")

        assert response.status_code == 401
        logger.info("Assertion passed: login returns 401.")
        assert response.json() == {"error": "Invalid credentials."}
        logger.info("Assertion passed: error message is 'Invalid credentials.'.")

