import unittest
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

if __name__ == '__main__':
    unittest.main()
