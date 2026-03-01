import unittest
from unittest.mock import MagicMock
import aiohttp
from pajgps_api import PajGpsApi

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
