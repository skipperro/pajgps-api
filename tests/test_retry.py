import unittest
from unittest.mock import patch, MagicMock
import requests
from pajgps_api.api import PajGpsApi
from pajgps_api.exceptions import RequestError

class TestRetryLogic(unittest.TestCase):
    def setUp(self):
        # Using short timeout for faster tests
        self.api = PajGpsApi("test@example.com", "password", timeout=0.1, max_retries=3)
        # Pre-set token to skip auto-login in _request
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_retry_on_timeout(self, mock_request):
        # Mock first two calls to time out, third to succeed
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": "ok"}
        
        mock_request.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            requests.exceptions.Timeout("Timeout 2"),
            mock_response
        ]
        
        # _request should call _execute_request (which we will implement)
        result = self.api._request("GET", "test-endpoint")
        
        self.assertEqual(result, {"success": "ok"})
        self.assertEqual(mock_request.call_count, 3)
        
        # Check increasing timeouts: 0.1s, 0.2s, 0.3s
        self.assertAlmostEqual(mock_request.call_args_list[0][1]['timeout'], 0.1)
        self.assertAlmostEqual(mock_request.call_args_list[1][1]['timeout'], 0.2)
        self.assertAlmostEqual(mock_request.call_args_list[2][1]['timeout'], 0.3)

    @patch('requests.Session.request')
    def test_retry_on_server_error(self, mock_request):
        # Mock first call to return 500, second to succeed
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"success": "ok"}
        
        mock_request.side_effect = [mock_response_500, mock_response_200]
        
        result = self.api._request("GET", "test-endpoint")
        
        self.assertEqual(result, {"success": "ok"})
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.Session.request')
    def test_max_retries_exceeded(self, mock_request):
        # Mock all calls to time out
        mock_request.side_effect = requests.exceptions.Timeout("Persistent timeout")
        
        with self.assertRaises(RequestError):
            self.api._request("GET", "test-endpoint")
        
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.Session.request')
    def test_no_retry_on_404(self, mock_request):
        # Mock 404 error
        mock_response_404 = MagicMock()
        mock_response_404.status_code = 404
        # requests.Session.request doesn't raise_for_status by default, 
        # but our _request method calls it after receiving response.
        mock_response_404.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response_404)
        
        mock_request.return_value = mock_response_404
        
        with self.assertRaises(RequestError):
            self.api._request("GET", "test-endpoint")
        
        # Should NOT retry on 404
        self.assertEqual(mock_request.call_count, 1)

if __name__ == '__main__':
    unittest.main()
