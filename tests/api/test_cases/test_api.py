# pytest -v -s -m debug tests/api/test_cases/test_api.py
import pytest
import requests
import time
import logging
logger = logging.getLogger(__name__)

class TestContact:

    @pytest.mark.debug
    def test_get_all_contacts(self):
        logger.info("Testing GET /contacts")

        url_base: str = "http://127.0.0.1:5000"
        endpoint_ping: str = "/ping"
        params = {"query": "python"}
        headers = {"Accept": "application/json"}

        response = requests.get(url_base + endpoint_ping, params=params, headers=headers)
        time.sleep(.5)
        assert response.status_code == 200, f"Failed to ping: Response code received: {response.status_code}. Expected: 200"
        logger.info(f"Pass: Response code received: {response.status_code}. Expected: 200")

        logger.info(f"Message: {response.text}, Type {type(response.text)}")
        logger.info(f"json: {response.json()}, Type {type(response.json())}")
        ping_response_text = response.text
        ping_response_json = response.json()
        logger.info(f"Type text {type(ping_response_text)}")
        logger.info(f"Type json {type(ping_response_json)}")
        assert ping_response_json["message"] == "Portfolio API is available.", f"Failed ping message"
        logger.info(f"Pass")

        endpoint_login = "/login" 
        autthentication_json: dict = {
             "username": "admin", "password": "password"
        }

        response_login = requests.post(url_base + endpoint_login, headers=headers, json=autthentication_json)
        time.sleep(.5)
        logger.info(f"Server Response to Login: {response_login}")
        logger.info(f"Login json {response_login.json()}")
        user_login_json = response_login.json()
        user_token = user_login_json['access_token']
        user_refresh_token = user_login_json['refresh_token']
        logger.info(f"The user token is {user_token}. Type: {type(user_token)}")
        logger.info(f"The user refresh token is {user_refresh_token}. Type: {type(user_refresh_token)}")
        
        if not isinstance(user_token, str):
           raise TypeError(f"Expected str, got {type(user_token).__name__}")
        if not isinstance(user_refresh_token, str):
           raise TypeError(f"Expected str, got {type(user_refresh_token).__name__}")

        endpoint_all_contacts = "/contacts"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {user_token}"
        }
        response_contacts = requests.get(url_base + endpoint_all_contacts, headers=headers)
        assert response_contacts.status_code == 200, f"Fail, Code received: {response_contacts.status_code}"
        logger.info(f"Pass, Code received: {response_contacts.status_code}")
        time.sleep(.5)
        logger.info(f"Server Response Contacts: {response_contacts}")
        logger.info(f"All contacts registered: {response_contacts.json()}")

