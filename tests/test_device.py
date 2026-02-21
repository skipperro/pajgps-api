import unittest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from dotenv import load_dotenv
import aiohttp
from pajgps_api.pajgps_api import PajGpsApi
from pajgps_api.pajgps_api_error import RequestError
from pajgps_api.models import Device

# Load environment variables from src/.env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'src', '.env')
load_dotenv(dotenv_path)


class TestGetDevices(unittest.IsolatedAsyncioTestCase):
    """Unit tests for get_devices (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_devices_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": [
                {"id": 1, "name": "Tracker A", "imei": "111111111111111"},
                {"id": 2, "name": "Tracker B", "imei": "222222222222222"},
            ]
        })
        mock_execute.return_value = mock_response

        result = await self.api.get_devices()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Device)
        self.assertEqual(result[0].name, "Tracker A")
        self.assertEqual(result[1].id, 2)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_devices_empty(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"success": []})
        mock_execute.return_value = mock_response

        result = await self.api.get_devices()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestGetDevice(unittest.IsolatedAsyncioTestCase):
    """Unit tests for get_device (mocked)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_device_by_id_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": {
                "id": 42,
                "name": "My GPS Tracker",
                "imei": "123456789012345",
                "model_nr": 9,
                "status": 1,
            }
        })
        mock_execute.return_value = mock_response

        result = await self.api.get_device(42)

        self.assertIsInstance(result, Device)
        self.assertEqual(result.id, 42)
        self.assertEqual(result.name, "My GPS Tracker")

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_device_not_found(self, mock_execute):
        mock_execute.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=404,
            message="Not Found",
        )

        with self.assertRaises(RequestError):
            await self.api.get_device(99999)


class TestUpdateDevice(unittest.IsolatedAsyncioTestCase):
    """Unit tests for update_device (mocked, no real API calls)."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_update_device_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": {
                "id": 42,
                "name": "Renamed Tracker",
                "imei": "123456789012345",
            }
        })
        mock_execute.return_value = mock_response

        result = await self.api.update_device(42, name="Renamed Tracker")

        self.assertIsInstance(result, Device)
        self.assertEqual(result.name, "Renamed Tracker")
        # Verify JSON body was sent
        call_kwargs = mock_execute.call_args[1]
        self.assertEqual(call_kwargs["json"], {"name": "Renamed Tracker"})

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_update_device_multiple_fields(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": {
                "id": 42,
                "name": "Updated",
                "spurfarbe": "#FF0000",
                "alarmintervall": 60,
            }
        })
        mock_execute.return_value = mock_response

        result = await self.api.update_device(42, name="Updated", spurfarbe="#FF0000", alarmintervall=60)

        self.assertEqual(result.spurfarbe, "#FF0000")
        self.assertEqual(result.alarmintervall, 60)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_update_device_permission_error(self, mock_execute):
        mock_execute.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=403,
            message="Forbidden",
        )

        with self.assertRaises(RequestError):
            await self.api.update_device(42, name="Should Fail")


class TestDeviceIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for device GET endpoints using real credentials."""

    def setUp(self):
        self.email = os.getenv("PAJGPS_EMAIL")
        self.password = os.getenv("PAJGPS_PASSWORD")
        self.api = PajGpsApi(self.email, self.password)

    async def asyncTearDown(self):
        await self.api.close()

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    async def test_real_get_devices(self):
        """Fetch all devices with real credentials."""
        await self.api.login()
        devices = await self.api.get_devices()

        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0, "Expected at least one device")
        first = devices[0]
        self.assertIsInstance(first, Device)
        self.assertTrue(hasattr(first, "id"))
        self.assertTrue(hasattr(first, "name"))
        self.assertTrue(hasattr(first, "imei"))
        print(f"\nFound {len(devices)} device(s). First: id={first.id}, name={first.name}")

    @unittest.skipIf(not os.getenv("PAJGPS_EMAIL") or not os.getenv("PAJGPS_PASSWORD"), "Credentials not found in .env")
    async def test_real_get_device_by_id(self):
        """Fetch a single device by ID with real credentials."""
        await self.api.login()
        devices = await self.api.get_devices()
        self.assertGreater(len(devices), 0, "Need at least one device to test get_device")

        device_id = devices[0].id
        device = await self.api.get_device(device_id)

        self.assertIsInstance(device, Device)
        self.assertEqual(device.id, device_id)
        self.assertTrue(hasattr(device, "name"))
        self.assertTrue(hasattr(device, "imei"))
        print(f"\nDevice {device_id}: name={device.name}, imei={device.imei}")


if __name__ == '__main__':
    unittest.main()
