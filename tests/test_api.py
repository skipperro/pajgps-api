import unittest
from unittest.mock import MagicMock
import aiohttp
from pajgps_api import PajGpsApi
from pajgps_api.alert_types import AlertType
from pajgps_api.pajgps_api import _normalize_alert_type


class TestNormalizeAlertType(unittest.TestCase):
    """Unit tests for the module-level _normalize_alert_type helper."""

    def test_alert_type_enum_is_converted_to_int(self):
        """AlertType enum values should be converted to their integer value."""
        result = _normalize_alert_type(AlertType.SOS)
        self.assertIsInstance(result, int)
        self.assertEqual(result, int(AlertType.SOS))

    def test_plain_int_is_returned_unchanged(self):
        """Plain integer values should be returned as-is."""
        self.assertEqual(_normalize_alert_type(5), 5)
        self.assertEqual(_normalize_alert_type(22), 22)


class TestGetHeadersWithoutToken(unittest.TestCase):
    def test_headers_without_token_have_no_authorization(self):
        """When no token is set, Authorization header should not be present."""
        api = PajGpsApi("test@example.com", "password")
        headers = api._get_headers()
        self.assertNotIn("Authorization", headers)
        self.assertEqual(headers.get("Accept"), "application/json")


class TestApiInit(unittest.TestCase):
    def test_api_init(self):
        api = PajGpsApi("test@example.com", "password")
        self.assertEqual(api.email, "test@example.com")
        self.assertEqual(api.password, "password")
        self.assertEqual(api.base_url, "https://connect.paj-gps.de/")

    def test_api_init_custom_base_url(self):
        api = PajGpsApi("test@example.com", "password", base_url="https://custom.api.example.com/")
        self.assertEqual(api.base_url, "https://custom.api.example.com/")

    def test_api_init_default_base_url_when_none(self):
        api = PajGpsApi("test@example.com", "password", base_url=None)
        self.assertEqual(api.base_url, "https://connect.paj-gps.de/")

    def test_api_init_with_websession(self):
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        api = PajGpsApi("test@example.com", "password", websession=mock_session)
        self.assertIs(api._session, mock_session)
        self.assertFalse(api._owns_session)

    def test_api_init_without_websession(self):
        api = PajGpsApi("test@example.com", "password")
        self.assertIsNone(api._session)
        self.assertTrue(api._owns_session)

if __name__ == '__main__':
    unittest.main()
