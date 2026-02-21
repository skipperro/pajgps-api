"""Tests that API methods raise PajGpsApiError on unexpected response formats.

Every public method should either return the correct typed result or raise
PajGpsApiError — never silently return a raw dict or wrong type.
"""

import unittest
from unittest.mock import patch, AsyncMock

from pajgps_api.pajgps_api import PajGpsApi
from pajgps_api.pajgps_api_error import PajGpsApiError


def _mock_response(payload: dict) -> AsyncMock:
    """Create a mock HTTP response that returns the given JSON payload."""
    response = AsyncMock()
    response.json = AsyncMock(return_value=payload)
    return response


class TestGetDevicesUnexpectedResponse(unittest.IsolatedAsyncioTestCase):
    """get_devices must return List[Device] or raise PajGpsApiError."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_missing_success_key(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "something"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_devices()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_success_is_dict_instead_of_list(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": {"id": 1}})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_devices()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_success_is_string(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": "unexpected"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_devices()


class TestGetDeviceUnexpectedResponse(unittest.IsolatedAsyncioTestCase):
    """get_device must return Device or raise PajGpsApiError."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_missing_success_key(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "not found"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_device(42)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_success_is_list_instead_of_dict(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": [{"id": 1}]})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_device(42)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_success_is_string(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": "unexpected"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_device(42)


class TestUpdateDeviceUnexpectedResponse(unittest.IsolatedAsyncioTestCase):
    """update_device must return Device or raise PajGpsApiError."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_missing_success_key(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "forbidden"})
        with self.assertRaises(PajGpsApiError):
            await self.api.update_device(42, name="Test")

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_success_is_list_instead_of_dict(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": [{"id": 42}]})
        with self.assertRaises(PajGpsApiError):
            await self.api.update_device(42, name="Test")


class TestTrackingDataUnexpectedResponse(unittest.IsolatedAsyncioTestCase):
    """Tracking data methods must return List[TrackPoint] or raise PajGpsApiError."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    # -- get_tracking_data_last_minutes --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_last_minutes_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_tracking_data_last_minutes(42, 60)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_last_minutes_success_is_dict(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": {"id": 1}})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_tracking_data_last_minutes(42, 60)

    # -- get_tracking_data_last_points --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_last_points_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_tracking_data_last_points(42, 5)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_last_points_success_is_string(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": "not a list"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_tracking_data_last_points(42, 5)

    # -- get_tracking_data_date_range --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_date_range_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_tracking_data_date_range(42, 1000, 2000)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_date_range_success_is_dict(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": {"data": "wrong"}})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_tracking_data_date_range(42, 1000, 2000)

    # -- get_all_last_positions --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_all_last_positions_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_all_last_positions([42])

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_all_last_positions_success_is_string(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": "nope"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_all_last_positions([42])


class TestSensorDataUnexpectedResponse(unittest.IsolatedAsyncioTestCase):
    """get_last_sensor_data must return SensorData or raise PajGpsApiError."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_missing_success_key(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "not found"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_last_sensor_data(42)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_success_is_list_instead_of_dict(self, mock_execute):
        """The real API can return an empty list when no sensor data exists."""
        mock_execute.return_value = _mock_response({"success": []})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_last_sensor_data(42)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_success_is_string(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": "unexpected"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_last_sensor_data(42)


class TestNotificationsUnexpectedResponse(unittest.IsolatedAsyncioTestCase):
    """Notification methods must return correct types or raise PajGpsApiError."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password123")
        self.api.token = "test_token"
        self.api.refresh_token = "test_refresh"

    async def asyncTearDown(self):
        await self.api.close()

    # -- get_notifications --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_notifications_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_notifications()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_notifications_success_is_dict(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": {"msg": "wrong"}})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_notifications()

    # -- get_device_notifications --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_device_notifications_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_device_notifications(42)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_device_notifications_success_is_string(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": "wrong"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_device_notifications(42)

    # -- get_custom_notifications --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_custom_notifications_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_custom_notifications(42, 1000, 2000)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_custom_notifications_success_is_dict(self, mock_execute):
        mock_execute.return_value = _mock_response({"success": {"msg": "wrong"}})
        with self.assertRaises(PajGpsApiError):
            await self.api.get_custom_notifications(42, 1000, 2000)

    # -- mark_notifications_read_by_device --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_mark_read_by_device_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.mark_notifications_read_by_device(42, 1)

    # -- mark_notifications_read_by_customer --

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_mark_read_by_customer_missing_success(self, mock_execute):
        mock_execute.return_value = _mock_response({"error": "bad"})
        with self.assertRaises(PajGpsApiError):
            await self.api.mark_notifications_read_by_customer(1)


if __name__ == '__main__':
    unittest.main()
