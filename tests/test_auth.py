import unittest
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
import requests
from pajgps_api.pajgps_api import PajGpsApi
from pajgps_api.pajgps_api_error import AuthenticationError, TokenRefreshError
from pajgps_api.models import AuthResponse

# Load environment variables from src/.env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'src', '.env')
load_dotenv(dotenv_path)

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")

    @patch('requests.Session.request')
    def test_login_success(self, mock_request):
        # Mocking successful login response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": {
                "token": "valid_token",
                "refresh_token": "valid_refresh_token",
                "userID": 123,
                "routeIcon": "circle"
            }
        }
        mock_request.return_value = mock_response

        result = self.api.login()

        self.assertIsInstance(result, AuthResponse)
        self.assertEqual(result.token, "valid_token")
        self.assertEqual(self.api.token, "valid_token")
        self.assertEqual(self.api.refresh_token, "valid_refresh_token")
        self.assertEqual(self.api.user_id, 123)
        mock_request.assert_called_once()

    @patch('requests.Session.request')
    def test_login_failure(self, mock_request):
        # Mocking failed login response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthenticated"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with self.assertRaises(AuthenticationError):
            self.api.login()

    @patch('requests.Session.request')
    def test_update_token_success(self, mock_request):
        self.api.refresh_token = "old_refresh_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": {
                "token": "new_token",
                "refresh_token": "new_refresh_token",
                "userID": 123,
                "routeIcon": "circle"
            }
        }
        mock_request.return_value = mock_response

        result = self.api.update_token()

        self.assertIsInstance(result, AuthResponse)
        self.assertEqual(result.token, "new_token")
        self.assertEqual(self.api.token, "new_token")
        self.assertEqual(self.api.refresh_token, "new_refresh_token")

    @patch('requests.Session.request')
    def test_update_token_failure(self, mock_request):
        self.api.refresh_token = "invalid_refresh_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthenticated"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with self.assertRaises(TokenRefreshError):
            self.api.update_token()

    @patch('requests.Session.request')
    @patch('pajgps_api.pajgps_api.PajGpsApi.update_token')
    def test_request_with_token_refresh(self, mock_update_token, mock_request):
        self.api.token = "expired_token"
        self.api.refresh_token = "valid_refresh_token"
        
        # The first call returns 401
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401
        
        # The second call returns 200
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"data": "success"}
        
        mock_request.side_effect = [mock_response_401, mock_response_200]
        
        result = self.api._request("GET", "test-endpoint")
        
        self.assertEqual(result, {"data": "success"})
        self.assertEqual(mock_request.call_count, 2)
        mock_update_token.assert_called_once()

class TestPreLoginBehavior(unittest.TestCase):
    """Tests for making requests before login."""

    def test_request_without_credentials_raises(self):
        """Calling _request with no token and no credentials should raise immediately."""
        api = PajGpsApi()
        with self.assertRaises(AuthenticationError) as ctx:
            api._request("GET", "api/v1/some-endpoint")
        self.assertIn("Not authenticated", str(ctx.exception))

    @patch('requests.Session.request')
    def test_request_auto_login_with_credentials(self, mock_request):
        """Calling _request with credentials but no token should auto-login first."""
        api = PajGpsApi("test@example.com", "password123")

        # First call: login response
        login_response = MagicMock()
        login_response.status_code = 200
        login_response.json.return_value = {
            "success": {
                "token": "auto_token",
                "refresh_token": "auto_refresh",
                "userID": 1,
                "routeIcon": "circle"
            }
        }

        # Second call: actual endpoint response
        endpoint_response = MagicMock()
        endpoint_response.status_code = 200
        endpoint_response.json.return_value = {"data": "result"}

        mock_request.side_effect = [login_response, endpoint_response]

        result = api._request("GET", "api/v1/some-endpoint")

        self.assertEqual(result, {"data": "result"})
        self.assertEqual(api.token, "auto_token")
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.Session.request')
    def test_401_with_no_refresh_token_tries_login(self, mock_request):
        """If 401 occurs and there's no refresh token but credentials exist, try login."""
        api = PajGpsApi("test@example.com", "password123")
        api.token = "stale_token"  # has a token but no refresh_token

        # First call: 401
        response_401 = MagicMock()
        response_401.status_code = 401

        # Login call succeeds
        login_response = MagicMock()
        login_response.status_code = 200
        login_response.json.return_value = {
            "success": {
                "token": "fresh_token",
                "refresh_token": "fresh_refresh",
                "userID": 1,
                "routeIcon": "circle"
            }
        }

        # Retry after login succeeds
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"data": "ok"}

        mock_request.side_effect = [response_401, login_response, success_response]

        result = api._request("GET", "api/v1/endpoint")
        self.assertEqual(result, {"data": "ok"})
        self.assertEqual(api.token, "fresh_token")


class TestAuthIntegration(unittest.TestCase):
    def setUp(self):
        self.email = os.getenv("PAJGPS_EMAIL")
        self.password = os.getenv("PAJGPS_PASSWORD")
        self.api = PajGpsApi(self.email, self.password)

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    def test_real_login(self):
        """Perform a real login using credentials from .env."""
        try:
            result = self.api.login()
            self.assertIsInstance(result, AuthResponse)
            self.assertTrue(hasattr(result, "token"))
            self.assertTrue(hasattr(result, "refresh_token"))
            self.assertTrue(hasattr(result, "userID"))
            self.assertIsNotNone(self.api.token)
            self.assertIsNotNone(self.api.refresh_token)
            print(f"\nLogin successful for user ID: {result.userID}")
        except AuthenticationError as e:
            self.fail(f"Real login failed: {str(e)}")

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    def test_real_update_token(self):
        """Perform a real token refresh using credentials from .env."""
        # First login
        try:
            self.api.login()
        except AuthenticationError as e:
            self.fail(f"Login failed before update_token test: {str(e)}")

        # Then refresh token
        try:
            result = self.api.update_token()
            self.assertIsInstance(result, AuthResponse)
            self.assertTrue(hasattr(result, "token"))
            self.assertTrue(hasattr(result, "refresh_token"))
            self.assertIsNotNone(self.api.token)
            self.assertIsNotNone(self.api.refresh_token)
            print("\nToken refresh successful")
        except TokenRefreshError as e:
            self.fail(f"Real token refresh failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()
