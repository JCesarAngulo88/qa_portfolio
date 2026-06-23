# pytest -v -s -m debug tests/api/test_cases/test_health.py
import logging
import pytest

from tests.api.config.api_endpoints import EndPoints
from tests.api.api_utils.data_factories import expected_health_payload

logger = logging.getLogger(__name__)


class TestHealthEndpoint:

    @pytest.mark.debug
    @pytest.mark.cont_test
    def test_ping_returns_expected_payload(self, api_client):
        logger.info(f"Starting health check test: verify GET {EndPoints.PING} returns 200 and the expected payload.")

        response = api_client.get(EndPoints.PING)
        logger.info(f"Received response from GET {EndPoints.PING}: {response.status_code}")

        assert response.status_code == 200, f"Failed, API response: {response.status_code}"
        logger.info(f"Assertion passed: status code is {response.status_code}")

        assert response.json() == expected_health_payload, f"Failed, API response: {response.json()} Expected payload: {expected_health_payload}"
        logger.info(f"Passed. Actual payload: {response.json()}.Expected payload: {expected_health_payload}")
