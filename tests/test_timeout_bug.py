import unittest
from unittest.mock import AsyncMock, MagicMock
import aiohttp
from pajgps_api.pajgps_api import PajGpsApi


def _make_mock_session(mock_request):
    """Create a mock aiohttp session with the given request mock."""
    session = MagicMock(spec=aiohttp.ClientSession)
    session.request = mock_request
    session.closed = False
    return session


class TestTimeoutBug(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password")
        self.api.token = "test_token"

    async def asyncTearDown(self):
        await self.api.close()

    async def test_timeout_override_does_not_crash(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={"success": "ok"})

        mock_request = AsyncMock(return_value=mock_response)
        self.api._session = _make_mock_session(mock_request)

        # This should NOT raise TypeError
        try:
            await self.api._request("GET", "test", timeout=10)
        except TypeError as e:
            self.fail(f"_request crashed with timeout override: {e}")

        self.assertEqual(mock_request.call_args[1]['timeout'].total, 10)


if __name__ == '__main__':
    unittest.main()
