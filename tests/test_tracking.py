import unittest
import os
import time
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from pajgps_api.pajgps_api import PajGpsApi
from pajgps_api.exceptions import RequestError
from pajgps_api.models import TrackPoint, SensorData

# Load environment variables from src/.env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'src', '.env')
load_dotenv(dotenv_path)


SAMPLE_TRACKING_POINT = {
    "id": "abc123",
    "lat": 50.792,
    "lng": 6.483,
    "direction": 180,
    "dateunix": 1700000000,
    "battery": 85,
    "speed": 30,
    "iddevice": 42,
    "steps": 0,
    "heartbeat": 0,
    "accuracy": 10,
    "wifi": None,
    "note": None,
    "upt": None,
    "wzp": False,
}


class TestGetTrackingDataLastMinutes(unittest.TestCase):
    """Unit tests for get_tracking_data_last_minutes (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_last_minutes_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": [SAMPLE_TRACKING_POINT]}
        mock_request.return_value = mock_response

        result = self.api.get_tracking_data_last_minutes(42, 60)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TrackPoint)
        self.assertEqual(result[0].lat, 50.792)
        # Verify URL and query params
        call_args = mock_request.call_args
        self.assertIn("/api/v1/trackerdata/42/last_minutes", call_args[0][1])
        self.assertEqual(call_args[1]["params"]["lastMinutes"], 60)

    @patch('requests.Session.request')
    def test_last_minutes_with_optional_params(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": [SAMPLE_TRACKING_POINT]}
        mock_request.return_value = mock_response

        result = self.api.get_tracking_data_last_minutes(42, 30, gps=1, wifi=0, sort="asc")

        call_params = mock_request.call_args[1]["params"]
        self.assertEqual(call_params["lastMinutes"], 30)
        self.assertEqual(call_params["gps"], 1)
        self.assertEqual(call_params["wifi"], 0)
        self.assertEqual(call_params["sort"], "asc")

    @patch('requests.Session.request')
    def test_last_minutes_empty(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": []}
        mock_request.return_value = mock_response

        result = self.api.get_tracking_data_last_minutes(42, 1)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestGetTrackingDataLastPoints(unittest.TestCase):
    """Unit tests for get_tracking_data_last_points (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_last_points_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": [SAMPLE_TRACKING_POINT, SAMPLE_TRACKING_POINT]}
        mock_request.return_value = mock_response

        result = self.api.get_tracking_data_last_points(42, 2)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], TrackPoint)
        call_args = mock_request.call_args
        self.assertIn("/api/v1/trackerdata/42/last_points", call_args[0][1])
        self.assertEqual(call_args[1]["params"]["lastPoints"], 2)

    @patch('requests.Session.request')
    def test_last_points_with_optional_params(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": [SAMPLE_TRACKING_POINT]}
        mock_request.return_value = mock_response

        self.api.get_tracking_data_last_points(42, 5, gps=1, wifi=1, sort="desc")

        call_params = mock_request.call_args[1]["params"]
        self.assertEqual(call_params["lastPoints"], 5)
        self.assertEqual(call_params["gps"], 1)
        self.assertEqual(call_params["wifi"], 1)
        self.assertEqual(call_params["sort"], "desc")


class TestGetTrackingDataDateRange(unittest.TestCase):
    """Unit tests for get_tracking_data_date_range (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_date_range_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": [SAMPLE_TRACKING_POINT]}
        mock_request.return_value = mock_response

        result = self.api.get_tracking_data_date_range(42, 1700000000, 1700003600)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TrackPoint)
        call_args = mock_request.call_args
        self.assertIn("/api/v1/trackerdata/42/date_range", call_args[0][1])
        call_params = call_args[1]["params"]
        self.assertEqual(call_params["dateStart"], 1700000000)
        self.assertEqual(call_params["dateEnd"], 1700003600)

    @patch('requests.Session.request')
    def test_date_range_with_optional_params(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": []}
        mock_request.return_value = mock_response

        self.api.get_tracking_data_date_range(42, 1700000000, 1700003600, gps=0, wifi=1, sort="asc")

        call_params = mock_request.call_args[1]["params"]
        self.assertEqual(call_params["gps"], 0)
        self.assertEqual(call_params["wifi"], 1)
        self.assertEqual(call_params["sort"], "asc")


class TestGetAllLastPositions(unittest.TestCase):
    """Unit tests for get_all_last_positions (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_all_last_positions_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": [SAMPLE_TRACKING_POINT],
            "number_of_records": 1,
        }
        mock_request.return_value = mock_response

        result = self.api.get_all_last_positions([42, 99])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TrackPoint)
        # Verify POST method and JSON body
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "POST")
        self.assertIn("/api/v1/trackerdata/getalllastpositions", call_args[0][1])
        self.assertEqual(call_args[1]["json"], {"deviceIDs": [42, 99], "fromLastPoint": False})

    @patch('requests.Session.request')
    def test_all_last_positions_with_from_last_point(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": [SAMPLE_TRACKING_POINT]}
        mock_request.return_value = mock_response

        self.api.get_all_last_positions([42], from_last_point=True)

        call_json = mock_request.call_args[1]["json"]
        self.assertEqual(call_json, {"deviceIDs": [42], "fromLastPoint": True})

    @patch('requests.Session.request')
    def test_all_last_positions_empty(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": [], "number_of_records": 0}
        mock_request.return_value = mock_response

        result = self.api.get_all_last_positions([99999])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestGetLastSensorData(unittest.TestCase):
    """Unit tests for get_last_sensor_data (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    @patch('requests.Session.request')
    def test_last_sensor_data_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": {
                "ts": {"$date": {"$numberLong": "1770996164000"}},
                "volt": 12410,
                "did": 42,
                "date_unix": {"$date": {"$numberLong": "1770940800000"}},
                "date_iso": "2026-02-13T15:22:44+00:00",
            }
        }
        mock_request.return_value = mock_response

        result = self.api.get_last_sensor_data(42)

        self.assertIsInstance(result, SensorData)
        self.assertEqual(result.volt, 12410)
        self.assertEqual(result.did, 42)
        call_args = mock_request.call_args
        self.assertIn("/api/v1/sensordata/last/42", call_args[0][1])

    @patch('requests.Session.request')
    def test_last_sensor_data_not_found(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = __import__('requests').exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with self.assertRaises(RequestError):
            self.api.get_last_sensor_data(99999)


class TestTrackingIntegration(unittest.TestCase):
    """Integration tests for tracking endpoints using real credentials."""

    def setUp(self):
        self.email = os.getenv("PAJGPS_EMAIL")
        self.password = os.getenv("PAJGPS_PASSWORD")
        self.api = PajGpsApi(self.email, self.password)

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    def test_real_get_tracking_last_points(self):
        """Fetch last tracking points with real credentials."""
        self.api.login()
        devices = self.api.get_devices()
        self.assertGreater(len(devices), 0, "Need at least one device")

        device_id = devices[0].id
        result = self.api.get_tracking_data_last_points(device_id, 3)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0, "Expected at least one tracking point")
        point = result[0]
        self.assertIsInstance(point, TrackPoint)
        self.assertTrue(hasattr(point, "lat"))
        self.assertTrue(hasattr(point, "lng"))
        self.assertTrue(hasattr(point, "dateunix"))
        print(f"\nDevice {device_id}: got {len(result)} tracking point(s). First: lat={point.lat}, lng={point.lng}")

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    def test_real_get_tracking_date_range(self):
        """Fetch tracking data by date range with real credentials."""
        self.api.login()
        devices = self.api.get_devices()
        self.assertGreater(len(devices), 0, "Need at least one device")

        device_id = devices[0].id
        now = int(time.time())
        one_hour_ago = now - 3600
        result = self.api.get_tracking_data_date_range(device_id, one_hour_ago, now)

        self.assertIsInstance(result, list)
        print(f"\nDevice {device_id}: got {len(result)} point(s) in last hour")

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    def test_real_get_all_last_positions(self):
        """Fetch all last positions with real credentials."""
        self.api.login()
        devices = self.api.get_devices()
        self.assertGreater(len(devices), 0, "Need at least one device")

        device_ids = [d.id for d in devices]
        result = self.api.get_all_last_positions(device_ids)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0, "Expected at least one position")
        point = result[0]
        self.assertIsInstance(point, TrackPoint)
        self.assertTrue(hasattr(point, "lat"))
        self.assertTrue(hasattr(point, "lng"))
        print(f"\nGot {len(result)} last position(s) for {len(device_ids)} device(s)")

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    def test_real_get_last_sensor_data(self):
        """Fetch last sensor data with real credentials."""
        self.api.login()
        devices = self.api.get_devices()
        self.assertGreater(len(devices), 0, "Need at least one device")

        device_id = devices[0].id
        result = self.api.get_last_sensor_data(device_id)

        # The API may return an object (with volt, did, etc.) or an empty list
        # if no sensor data is available for the device.
        if isinstance(result, SensorData):
            self.assertTrue(hasattr(result, "volt"))
            self.assertTrue(hasattr(result, "did"))
            print(f"\nDevice {device_id}: voltage={result.volt}mV")
        else:
            self.assertIsInstance(result, list)
            print(f"\nDevice {device_id}: no sensor data available")


if __name__ == '__main__':
    unittest.main()
