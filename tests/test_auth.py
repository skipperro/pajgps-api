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

class TestLoginEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Tests for login() edge cases: missing credentials and network failures."""

    async def asyncTearDown(self):
        if hasattr(self, "api"):
            await self.api.close()

    async def test_login_raises_when_no_credentials(self):
        """login() should raise AuthenticationError when no email/password is set."""
        self.api = PajGpsApi()
        with self.assertRaises(AuthenticationError) as ctx:
            await self.api.login()
        self.assertIn("Email and password are required", str(ctx.exception))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_login_raises_on_client_error(self, mock_execute):
        """login() should wrap aiohttp.ClientError into AuthenticationError."""
        self.api = PajGpsApi("test@example.com", "password")
        mock_execute.side_effect = aiohttp.ClientError("connection refused")
        with self.assertRaises(AuthenticationError) as ctx:
            await self.api.login()
        self.assertIn("Request failed", str(ctx.exception))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_login_raises_on_error_response(self, mock_execute):
        """login() should raise AuthenticationError when the response contains 'error' key."""
        self.api = PajGpsApi("test@example.com", "password")
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"error": "Invalid credentials"})
        mock_execute.return_value = mock_response
        with self.assertRaises(AuthenticationError) as ctx:
            await self.api.login()
        self.assertIn("Login failed", str(ctx.exception))


class TestUpdateTokenEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Tests for update_token() edge cases: missing credentials and network failures."""

    async def asyncTearDown(self):
        if hasattr(self, "api"):
            await self.api.close()

    async def test_update_token_raises_when_no_email(self):
        """update_token() should raise TokenRefreshError when email is missing."""
        self.api = PajGpsApi()
        self.api.refresh_token = "some_refresh_token"
        with self.assertRaises(TokenRefreshError) as ctx:
            await self.api.update_token()
        self.assertIn("Email and refresh token are required", str(ctx.exception))

    async def test_update_token_raises_when_no_refresh_token(self):
        """update_token() should raise TokenRefreshError when refresh_token is missing."""
        self.api = PajGpsApi("test@example.com", "password")
        with self.assertRaises(TokenRefreshError) as ctx:
            await self.api.update_token()
        self.assertIn("Email and refresh token are required", str(ctx.exception))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_update_token_raises_on_client_error(self, mock_execute):
        """update_token() should wrap aiohttp.ClientError into TokenRefreshError."""
        self.api = PajGpsApi("test@example.com", "password")
        self.api.refresh_token = "valid_refresh_token"
        mock_execute.side_effect = aiohttp.ClientError("connection refused")
        with self.assertRaises(TokenRefreshError) as ctx:
            await self.api.update_token()
        self.assertIn("Request failed", str(ctx.exception))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_update_token_raises_on_error_response(self, mock_execute):
        """update_token() should raise TokenRefreshError when the response contains 'error' key."""
        self.api = PajGpsApi("test@example.com", "password")
        self.api.refresh_token = "valid_refresh_token"
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"error": "Invalid refresh token"})
        mock_execute.return_value = mock_response
        with self.assertRaises(TokenRefreshError) as ctx:
            await self.api.update_token()
        self.assertIn("Token refresh failed", str(ctx.exception))


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


def _make_session(side_effects):
    """Build a mock aiohttp.ClientSession whose request() yields the given side_effects."""
    session = MagicMock(spec=aiohttp.ClientSession)
    session.closed = False
    session.request = AsyncMock(side_effect=side_effects)
    return session


def _make_response(status, json_payload=None, raise_on_raise_for_status=False):
    resp = MagicMock()
    resp.status = status
    if raise_on_raise_for_status:
        err = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=status
        )
        resp.raise_for_status = MagicMock(side_effect=err)
    else:
        resp.raise_for_status = MagicMock()
    if json_payload is not None:
        resp.json = AsyncMock(return_value=json_payload)
    return resp


class TestExecuteRequest401Branches(unittest.IsolatedAsyncioTestCase):
    """Cover the 401-handling inner block in _execute_request."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password", timeout=1, max_retries=2)
        self.api.token = "old_token"
        self.api.refresh_token = "valid_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_api.PajGpsApi.update_token", new_callable=AsyncMock)
    async def test_401_triggers_token_refresh_then_retries(self, mock_update_token):
        """On 401, _execute_request should call update_token and retry the request."""
        mock_update_token.return_value = None
        resp_401 = _make_response(401)
        resp_200 = _make_response(200, json_payload={"success": "ok"})
        self.api._session = _make_session([resp_401, resp_200])

        url = f"{self.api.base_url.rstrip('/')}/api/v1/test"
        result = await self.api._execute_request("GET", url, refresh_on_401=True)

        mock_update_token.assert_called_once()
        self.assertEqual(result.status, 200)

    @patch("pajgps_api.pajgps_api.PajGpsApi.update_token", new_callable=AsyncMock)
    @patch("pajgps_api.pajgps_api.PajGpsApi.login", new_callable=AsyncMock)
    async def test_401_falls_back_to_login_when_refresh_fails(self, mock_login, mock_update_token):
        """When update_token raises TokenRefreshError, login() should be attempted."""
        mock_update_token.side_effect = TokenRefreshError("expired")
        mock_login.return_value = None
        resp_401 = _make_response(401)
        resp_200 = _make_response(200, json_payload={"success": "ok"})
        self.api._session = _make_session([resp_401, resp_200])

        url = f"{self.api.base_url.rstrip('/')}/api/v1/test"
        await self.api._execute_request("GET", url, refresh_on_401=True)

        mock_update_token.assert_called_once()
        mock_login.assert_called_once()

    @patch("pajgps_api.pajgps_api.PajGpsApi.login", new_callable=AsyncMock)
    async def test_401_with_no_refresh_token_calls_login(self, mock_login):
        """When there is no refresh_token but credentials exist, login() should be called."""
        self.api.refresh_token = None
        mock_login.return_value = None
        resp_401 = _make_response(401)
        resp_200 = _make_response(200, json_payload={"success": "ok"})
        self.api._session = _make_session([resp_401, resp_200])

        url = f"{self.api.base_url.rstrip('/')}/api/v1/test"
        await self.api._execute_request("GET", url, refresh_on_401=True)

        mock_login.assert_called_once()

    async def test_401_with_no_credentials_and_no_refresh_raises(self):
        """When no refresh_token and no credentials, the 401 response causes raise_for_status to raise."""
        self.api.token = None
        self.api.refresh_token = None
        self.api.email = None
        self.api.password = None
        resp_401 = _make_response(401, raise_on_raise_for_status=True)
        self.api._session = _make_session([resp_401])

        url = f"{self.api.base_url.rstrip('/')}/api/v1/test"
        with self.assertRaises(aiohttp.ClientResponseError):
            await self.api._execute_request("GET", url, refresh_on_401=True)


class TestExecuteRequest401NoCredentials(unittest.IsolatedAsyncioTestCase):
    """Cover the 'else: raise' path when update_token fails and no email/password."""

    def setUp(self):
        self.api = PajGpsApi(timeout=1, max_retries=1)
        self.api.token = "old_token"
        self.api.refresh_token = "some_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_api.PajGpsApi.update_token", new_callable=AsyncMock)
    async def test_token_refresh_error_re_raised_when_no_credentials(self, mock_update_token):
        """When update_token raises and there are no credentials, the error re-raises."""
        mock_update_token.side_effect = TokenRefreshError("expired")
        resp_401 = _make_response(401, raise_on_raise_for_status=True)
        self.api._session = _make_session([resp_401])

        url = f"{self.api.base_url.rstrip('/')}/api/v1/test"
        with self.assertRaises((TokenRefreshError, aiohttp.ClientResponseError)):
            await self.api._execute_request("GET", url, refresh_on_401=True)


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
