import unittest
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from pajgps_api.api import PajGpsApi
from pajgps_api.exceptions import AuthenticationError, RequestError

# Load environment variables from src/.env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'src', '.env')
load_dotenv(dotenv_path)


class TestGetDevices(unittest.TestCase):
    """Unit tests for get_devices (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_get_devices_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": [
                {"id": 1, "name": "Tracker A", "imei": "111111111111111"},
                {"id": 2, "name": "Tracker B", "imei": "222222222222222"},
            ]
        }
        mock_request.return_value = mock_response

        result = self.api.get_devices()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Tracker A")
        self.assertEqual(result[1]["id"], 2)

    @patch('requests.Session.request')
    def test_get_devices_empty(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": []}
        mock_request.return_value = mock_response

        result = self.api.get_devices()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestGetDevice(unittest.TestCase):
    """Unit tests for get_device (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_get_device_by_id_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": {
                "id": 42,
                "name": "My GPS Tracker",
                "imei": "123456789012345",
                "model_nr": 9,
                "status": 1,
            }
        }
        mock_request.return_value = mock_response

        result = self.api.get_device(42)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], 42)
        self.assertEqual(result["name"], "My GPS Tracker")
        # Verify correct URL was called
        call_url = mock_request.call_args[0][1]
        self.assertIn("/api/v1/device/42", call_url)

    @patch('requests.Session.request')
    def test_get_device_not_found(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = __import__('requests').exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with self.assertRaises(RequestError):
            self.api.get_device(99999)


class TestUpdateDevice(unittest.TestCase):
    """Unit tests for update_device (mocked, no real API calls)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_update_device_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": {
                "id": 42,
                "name": "Renamed Tracker",
                "imei": "123456789012345",
            }
        }
        mock_request.return_value = mock_response

        result = self.api.update_device(42, name="Renamed Tracker")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "Renamed Tracker")
        # Verify PUT method and URL
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "PUT")
        self.assertIn("/api/v1/device/42", call_args[0][1])
        # Verify JSON body was sent
        self.assertEqual(call_args[1]["json"], {"name": "Renamed Tracker"})

    @patch('requests.Session.request')
    def test_update_device_multiple_fields(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": {
                "id": 42,
                "name": "Updated",
                "spurfarbe": "#FF0000",
                "alarmintervall": 60,
            }
        }
        mock_request.return_value = mock_response

        result = self.api.update_device(42, name="Updated", spurfarbe="#FF0000", alarmintervall=60)

        self.assertEqual(result["spurfarbe"], "#FF0000")
        self.assertEqual(result["alarmintervall"], 60)
        call_json = mock_request.call_args[1]["json"]
        self.assertEqual(call_json, {"name": "Updated", "spurfarbe": "#FF0000", "alarmintervall": 60})

    @patch('requests.Session.request')
    def test_update_device_permission_error(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = __import__('requests').exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with self.assertRaises(RequestError):
            self.api.update_device(42, name="Should Fail")


class TestDeviceIntegration(unittest.TestCase):
    """Integration tests for device GET endpoints using real credentials."""

    def setUp(self):
        self.email = os.getenv("PAJGPS_EMAIL")
        self.password = os.getenv("PAJGPS_PASSWORD")
        self.api = PajGpsApi(self.email, self.password)

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    def test_real_get_devices(self):
        """Fetch all devices with real credentials."""
        self.api.login()
        devices = self.api.get_devices()

        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0, "Expected at least one device")
        # Each device should have basic fields
        first = devices[0]
        self.assertIn("id", first)
        self.assertIn("name", first)
        self.assertIn("imei", first)
        print(f"\nFound {len(devices)} device(s). First: id={first['id']}, name={first['name']}")

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    def test_real_get_device_by_id(self):
        """Fetch a single device by ID with real credentials."""
        self.api.login()
        devices = self.api.get_devices()
        self.assertGreater(len(devices), 0, "Need at least one device to test get_device")

        device_id = devices[0]["id"]
        device = self.api.get_device(device_id)

        self.assertIsInstance(device, dict)
        self.assertEqual(device["id"], device_id)
        self.assertIn("name", device)
        self.assertIn("imei", device)
        print(f"\nDevice {device_id}: name={device['name']}, imei={device['imei']}")


if __name__ == '__main__':
    unittest.main()
