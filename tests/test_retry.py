import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock
import aiohttp
from pajgps_api.pajgps_api import PajGpsApi
from pajgps_api.pajgps_api_error import RequestError


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


if __name__ == '__main__':
    unittest.main()
