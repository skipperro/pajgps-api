import unittest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from dotenv import load_dotenv
import aiohttp
from pajgps_api.pajgps_api import PajGpsApi
from pajgps_api.pajgps_api_error import AuthenticationError, TokenRefreshError
from pajgps_api.models import AuthResponse

# Load environment variables from src/.env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'src', '.env')
load_dotenv(dotenv_path)

class TestAuth(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_login_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": {
                "token": "valid_token",
                "refresh_token": "valid_refresh_token",
                "userID": 123,
                "routeIcon": "circle"
            }
        })
        mock_execute.return_value = mock_response

        result = await self.api.login()

        self.assertIsInstance(result, AuthResponse)
        self.assertEqual(result.token, "valid_token")
        self.assertEqual(self.api.token, "valid_token")
        self.assertEqual(self.api.refresh_token, "valid_refresh_token")
        self.assertEqual(self.api.user_id, 123)
        mock_execute.assert_called_once()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_login_failure(self, mock_execute):
        mock_execute.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=401,
            message="Unauthorized",
        )

        with self.assertRaises(AuthenticationError):
            await self.api.login()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_update_token_success(self, mock_execute):
        self.api.refresh_token = "old_refresh_token"

        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": {
                "token": "new_token",
                "refresh_token": "new_refresh_token",
                "userID": 123,
                "routeIcon": "circle"
            }
        })
        mock_execute.return_value = mock_response

        result = await self.api.update_token()

        self.assertIsInstance(result, AuthResponse)
        self.assertEqual(result.token, "new_token")
        self.assertEqual(self.api.token, "new_token")
        self.assertEqual(self.api.refresh_token, "new_refresh_token")

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_update_token_failure(self, mock_execute):
        self.api.refresh_token = "invalid_refresh_token"

        mock_execute.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=401,
            message="Unauthorized",
        )

        with self.assertRaises(TokenRefreshError):
            await self.api.update_token()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_request_with_token_refresh(self, mock_execute):
        self.api.token = "expired_token"
        self.api.refresh_token = "valid_refresh_token"

        # First call: the endpoint response (after auto-refresh handled inside _execute_request)
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"data": "success"})
        mock_execute.return_value = mock_response

        result = await self.api._request("GET", "test-endpoint")

        self.assertEqual(result, {"data": "success"})


class TestPreLoginBehavior(unittest.IsolatedAsyncioTestCase):
    """Tests for making requests before login."""

    async def asyncTearDown(self):
        if hasattr(self, 'api'):
            await self.api.close()

    async def test_request_without_credentials_raises(self):
        """Calling _request with no token and no credentials should raise immediately."""
        self.api = PajGpsApi()
        with self.assertRaises(AuthenticationError) as ctx:
            await self.api._request("GET", "api/v1/some-endpoint")
        self.assertIn("Not authenticated", str(ctx.exception))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_request_auto_login_with_credentials(self, mock_execute):
        """Calling _request with credentials but no token should auto-login first."""
        self.api = PajGpsApi("test@example.com", "password123")

        # First call: login response
        login_response = AsyncMock()
        login_response.json = AsyncMock(return_value={
            "success": {
                "token": "auto_token",
                "refresh_token": "auto_refresh",
                "userID": 1,
                "routeIcon": "circle"
            }
        })

        # Second call: actual endpoint response
        endpoint_response = AsyncMock()
        endpoint_response.json = AsyncMock(return_value={"data": "result"})

        mock_execute.side_effect = [login_response, endpoint_response]

        result = await self.api._request("GET", "api/v1/some-endpoint")

        self.assertEqual(result, {"data": "result"})
        self.assertEqual(self.api.token, "auto_token")

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_401_with_no_refresh_token_tries_login(self, mock_execute):
        """If 401 occurs and there's no refresh token but credentials exist, try login."""
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "stale_token"  # has a token but no refresh_token

        # The endpoint response (after auto-refresh handled inside _execute_request)
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"data": "ok"})
        mock_execute.return_value = mock_response

        result = await self.api._request("GET", "api/v1/endpoint")
        self.assertEqual(result, {"data": "ok"})


class TestAuthIntegration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.email = os.getenv("PAJGPS_EMAIL")
        self.password = os.getenv("PAJGPS_PASSWORD")
        self.api = PajGpsApi(self.email, self.password)

    async def asyncTearDown(self):
        await self.api.close()

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    async def test_real_login(self):
        """Perform a real login using credentials from .env."""
        try:
            result = await self.api.login()
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
    async def test_real_update_token(self):
        """Perform a real token refresh using credentials from .env."""
        try:
            await self.api.login()
        except AuthenticationError as e:
            self.fail(f"Login failed before update_token test: {str(e)}")

        try:
            result = await self.api.update_token()
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
