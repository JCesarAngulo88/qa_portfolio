# pytest -v -s -m debug tests/api/test_cases/test_contacts.py

import logging
import pytest

from tests.api.config.api_endpoints import EndPoints

logger = logging.getLogger(__name__)


class TestContactsEndpoints:

    @pytest.mark.debug
    @pytest.mark.cont_test
    def test_create_contact_with_valid_payload(self, authenticated_client):

        logger.info("Starting contact creation test: verify a valid payload creates a new contact.")

        payload = {
            "full_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "555-0101",
            "company": "QA Labs",
            "subject": "Pytest contact",
            "message": "Hello from the API test suite.",
        }

        response = authenticated_client.post(EndPoints.CONTACTS, json=payload)

        logger.info(f"Create contact response status: {response.status_code}, body: {response.json()}")

        assert response.status_code == 201
        logger.info("Assertion passed: creation returns 201.")
        body = response.json()
        assert body["contact"]["full_name"] == payload["full_name"]
        assert body["contact"]["email"] == payload["email"]
        assert body["contact"]["message"] == payload["message"]

    @pytest.mark.debug
    @pytest.mark.cont_test
    def test_read_all_registers(self, authenticated_client):
        logger.info(f"Test Case Get All contacts registered")

        response = authenticated_client.get(EndPoints.CONTACTS)

        assert response.status_code == 200

