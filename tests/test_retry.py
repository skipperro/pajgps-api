import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from pajgps_api.pajgps_api import PajGpsApi
from pajgps_api.pajgps_api_error import AuthenticationError, RequestError


def _make_mock_session(mock_request):
    """Create a mock aiohttp session with the given request mock."""
    session = MagicMock(spec=aiohttp.ClientSession)
    session.request = mock_request
    session.closed = False
    return session


class TestRetryLogic(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Using short timeout for faster tests
        self.api = PajGpsApi("test@example.com", "password", timeout=1, max_retries=3)
        # Pre-set token to skip auto-login in _request
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    async def test_retry_on_timeout(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={"success": "ok"})

        mock_request = AsyncMock(side_effect=[
            asyncio.TimeoutError(),
            asyncio.TimeoutError(),
            mock_response,
        ])
        self.api._session = _make_mock_session(mock_request)

        result = await self.api._request("GET", "test-endpoint")

        self.assertEqual(result, {"success": "ok"})
        self.assertEqual(mock_request.call_count, 3)

        # Check increasing timeouts: 1s, 2s, 3s
        for i, call in enumerate(mock_request.call_args_list, start=1):
            self.assertEqual(call[1]["timeout"].total, i)

    async def test_retry_on_server_error(self):
        mock_response_500 = MagicMock()
        mock_response_500.status = 500

        mock_response_200 = MagicMock()
        mock_response_200.status = 200
        mock_response_200.raise_for_status = MagicMock()
        mock_response_200.json = AsyncMock(return_value={"success": "ok"})

        mock_request = AsyncMock(side_effect=[mock_response_500, mock_response_200])
        self.api._session = _make_mock_session(mock_request)

        result = await self.api._request("GET", "test-endpoint")

        self.assertEqual(result, {"success": "ok"})
        self.assertEqual(mock_request.call_count, 2)

    async def test_max_retries_exceeded(self):
        mock_request = AsyncMock(side_effect=asyncio.TimeoutError())
        self.api._session = _make_mock_session(mock_request)

        with self.assertRaises(RequestError):
            await self.api._request("GET", "test-endpoint")

        self.assertEqual(mock_request.call_count, 3)

    async def test_no_retry_on_404(self):
        mock_response_404 = MagicMock()
        mock_response_404.status = 404
        mock_response_404.raise_for_status = MagicMock(
            side_effect=aiohttp.ClientResponseError(
                request_info=MagicMock(),
                history=(),
                status=404,
                message="Not Found",
            )
        )

        mock_request = AsyncMock(return_value=mock_response_404)
        self.api._session = _make_mock_session(mock_request)

        with self.assertRaises(RequestError):
            await self.api._request("GET", "test-endpoint")

        # Should NOT retry on 404
        self.assertEqual(mock_request.call_count, 1)


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


class TestRequestErrorPaths(unittest.IsolatedAsyncioTestCase):
    """Cover error propagation paths inside _request()."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password", timeout=1, max_retries=1)
        self.api.token = "test_token"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_request_raises_authentication_error_on_401_response(self, mock_execute):
        """_request() should raise AuthenticationError when a 401 ClientResponseError propagates."""
        err = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=401, message="Unauthorized"
        )
        mock_execute.side_effect = err
        with self.assertRaises(AuthenticationError):
            await self.api._request("GET", "api/v1/some-endpoint")

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_request_raises_request_error_on_client_error(self, mock_execute):
        """_request() should raise RequestError when an aiohttp.ClientError propagates."""
        mock_execute.side_effect = aiohttp.ClientError("network error")
        with self.assertRaises(RequestError):
            await self.api._request("GET", "api/v1/some-endpoint")

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_request_raises_request_error_on_timeout(self, mock_execute):
        """_request() should raise RequestError when an asyncio.TimeoutError propagates."""
        mock_execute.side_effect = asyncio.TimeoutError()
        with self.assertRaises(RequestError):
            await self.api._request("GET", "api/v1/some-endpoint")

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_request_raises_request_error_on_non_401_response_error(self, mock_execute):
        """_request() should raise RequestError for non-401 ClientResponseError."""
        err = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=500, message="Server Error"
        )
        mock_execute.side_effect = err
        with self.assertRaises(RequestError):
            await self.api._request("GET", "api/v1/some-endpoint")


class TestExecuteRequestEdgePaths(unittest.IsolatedAsyncioTestCase):
    """Cover edge paths inside _execute_request for retry-status and connection errors."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password", timeout=1, max_retries=2)
        self.api.token = "test_token"

    async def asyncTearDown(self):
        await self.api.close()

    async def test_retry_status_raises_on_last_attempt(self):
        """When a retry-status code is returned on the last attempt, raise_for_status is called."""
        resp_503 = _make_response(503, raise_on_raise_for_status=True)
        self.api._session = _make_mock_session(AsyncMock(side_effect=[resp_503, resp_503]))

        url = f"{self.api.base_url.rstrip('/')}/api/v1/test"
        with self.assertRaises(aiohttp.ClientResponseError) as ctx:
            await self.api._execute_request("GET", url, refresh_on_401=False)
        self.assertEqual(ctx.exception.status, 503)

    async def test_connection_error_raises_on_last_attempt(self):
        """ClientConnectionError on every attempt should raise after max_retries."""
        conn_err = aiohttp.ClientConnectionError("refused")
        self.api._session = _make_mock_session(AsyncMock(side_effect=[conn_err, conn_err]))

        url = f"{self.api.base_url.rstrip('/')}/api/v1/test"
        with self.assertRaises(aiohttp.ClientConnectionError):
            await self.api._execute_request("GET", url, refresh_on_401=False)


if __name__ == '__main__':
    unittest.main()
