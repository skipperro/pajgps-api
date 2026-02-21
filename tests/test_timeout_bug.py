import unittest
from unittest.mock import patch, MagicMock
from pajgps_api.pajgps_api import PajGpsApi

class TestTimeoutBug(unittest.TestCase):
    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password")
        self.api.token = "test_token"

    @patch('requests.Session.request')
    def test_timeout_override_does_not_crash(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": "ok"}
        mock_request.return_value = mock_response

        # This should NOT raise TypeError: request() got multiple values for argument 'timeout'
        try:
            self.api._request("GET", "test", timeout=10)
        except TypeError as e:
            self.fail(f"_request crashed with timeout override: {e}")
        
        self.assertEqual(mock_request.call_args[1]['timeout'], 10)

if __name__ == '__main__':
    unittest.main()
