import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from pajgps_api.pajgps_api import PajGpsApi


def _make_mock_session(mock_request=None, closed=False):
    """Create a mock aiohttp.ClientSession."""
    session = MagicMock(spec=aiohttp.ClientSession)
    session.closed = closed
    if mock_request is not None:
        session.request = mock_request
    session.close = AsyncMock()
    return session


class TestWebsessionInjection(unittest.IsolatedAsyncioTestCase):
    """Tests for the external websession parameter."""

    def test_no_websession_owns_session(self):
        """When no websession is passed, the library should own the session."""
        api = PajGpsApi("test@example.com", "password")
        self.assertIsNone(api._session)
        self.assertTrue(api._owns_session)

    def test_websession_stored_and_not_owned(self):
        """When a websession is passed, it is stored and not owned."""
        mock_session = _make_mock_session()
        api = PajGpsApi("test@example.com", "password", websession=mock_session)
        self.assertIs(api._session, mock_session)
        self.assertFalse(api._owns_session)

    def test_websession_with_keyword_args(self):
        """Ensure the Home Assistant-style keyword constructor works."""
        mock_session = _make_mock_session()
        api = PajGpsApi(
            email="test@example.com",
            password="password",
            websession=mock_session,
        )
        self.assertIs(api._session, mock_session)
        self.assertFalse(api._owns_session)
        self.assertEqual(api.email, "test@example.com")


class TestGetSessionWithWebsession(unittest.IsolatedAsyncioTestCase):
    """Tests for _get_session behaviour with an injected websession."""

    async def test_get_session_returns_injected_session(self):
        """_get_session should return the injected session without creating a new one."""
        mock_session = _make_mock_session()
        api = PajGpsApi("test@example.com", "password", websession=mock_session)

        session = await api._get_session()

        self.assertIs(session, mock_session)
        self.assertFalse(api._owns_session)

    @patch("pajgps_api.pajgps_requests.aiohttp.ClientSession")
    async def test_get_session_creates_session_when_none(self, mock_cls):
        """_get_session should create a new session when none is provided."""
        new_session = MagicMock()
        new_session.closed = False
        new_session.close = AsyncMock()
        mock_cls.return_value = new_session

        api = PajGpsApi("test@example.com", "password")
        session = await api._get_session()

        self.assertIs(session, new_session)
        self.assertTrue(api._owns_session)
        mock_cls.assert_called_once()

        await api.close()


class TestCloseWithWebsession(unittest.IsolatedAsyncioTestCase):
    """Tests for close() behaviour depending on session ownership."""

    async def test_close_does_not_close_external_session(self):
        """close() must NOT call .close() on an externally provided session."""
        mock_session = _make_mock_session()
        api = PajGpsApi("test@example.com", "password", websession=mock_session)

        await api.close()

        mock_session.close.assert_not_called()
        # Session reference should be cleared
        self.assertIsNone(api._session)

    async def test_close_closes_internal_session(self):
        """close() must call .close() on an internally created session."""
        mock_session = _make_mock_session()

        api = PajGpsApi("test@example.com", "password")
        api._session = mock_session
        api._owns_session = True

        await api.close()

        mock_session.close.assert_called_once()
        self.assertIsNone(api._session)


class TestRequestUsesWebsession(unittest.IsolatedAsyncioTestCase):
    """Tests that requests flow through the injected websession."""

    async def test_request_uses_injected_session(self):
        """A request should be dispatched via the injected websession."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={"success": "ok"})

        mock_request = AsyncMock(return_value=mock_response)
        mock_session = _make_mock_session(mock_request)

        api = PajGpsApi("test@example.com", "password", websession=mock_session)
        api.token = "test_token"

        result = await api._request("GET", "test-endpoint")

        self.assertEqual(result, {"success": "ok"})
        mock_request.assert_called_once()
        # Verify the session used is the one we injected
        self.assertIs(api._session, mock_session)

    async def asyncTearDown(self):
        # Nothing to tear down — external sessions are not closed
        pass


class TestCloseEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Tests for close() edge-case behaviour."""

    async def test_close_when_session_is_none_does_not_raise(self):
        """close() when _session is None should complete without error."""
        api = PajGpsApi("test@example.com", "password")
        api._session = None
        await api.close()

    async def test_close_when_session_already_closed_does_not_raise(self):
        """close() when _session is already closed should not call close() again."""
        api = PajGpsApi("test@example.com", "password")
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        mock_session.closed = True
        mock_session.close = AsyncMock()
        api._session = mock_session
        api._owns_session = True

        await api.close()

        mock_session.close.assert_not_called()

    async def test_close_sets_session_to_none(self):
        """close() should set _session to None after closing."""
        api = PajGpsApi("test@example.com", "password")
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        mock_session.closed = False
        mock_session.close = AsyncMock()
        api._session = mock_session
        api._owns_session = True

        await api.close()

        self.assertIsNone(api._session)


class TestContextManager(unittest.IsolatedAsyncioTestCase):
    """Cover the async context-manager protocol on PajGpsApi."""

    async def test_aenter_returns_self(self):
        """__aenter__ should return the api instance itself."""
        api = PajGpsApi("test@example.com", "password")
        result = await api.__aenter__()
        self.assertIs(result, api)
        await api.close()

    async def test_aexit_closes_session(self):
        """__aexit__ should call close(), setting _session to None."""
        api = PajGpsApi("test@example.com", "password")
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        mock_session.closed = False
        mock_session.close = AsyncMock()
        api._session = mock_session
        api._owns_session = True

        await api.__aexit__(None, None, None)

        mock_session.close.assert_called_once()
        self.assertIsNone(api._session)

    async def test_async_context_manager_usage(self):
        """Using 'async with' syntax should work correctly."""
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        mock_session.closed = False
        mock_session.close = AsyncMock()

        async with PajGpsApi("test@example.com", "password") as api:
            api._session = mock_session
            api._owns_session = True
            self.assertIsNotNone(api)

        mock_session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
