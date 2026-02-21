import unittest
from pajgps_api import PajGpsApi

class TestApiInit(unittest.TestCase):
    def test_api_init(self):
        api = PajGpsApi("test@example.com", "password")
        self.assertEqual(api.email, "test@example.com")
        self.assertEqual(api.password, "password")
        self.assertEqual(api.base_url, "https://connect.paj-gps.de/")

if __name__ == '__main__':
    unittest.main()
