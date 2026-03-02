import unittest
from unittest.mock import patch, AsyncMock
from pajgps_api import PajGpsApi
from pajgps_api.alert_types import AlertType
from pajgps_api.models import Notification


def _notification_payload():
    return {
        "success": [
            {
                "id": 1, "iddevice": 10, "icon": "icon", "bezeichnung": "Alert",
                "meldungtyp": 1, "dateunix": 1234567890, "lat": 1.0, "lng": 2.0,
                "isread": 0, "radiusin": 0, "radiusout": 0,
                "zuendon": 0, "zuendoff": 0, "push": 1, "suppressed": 0,
            }
        ]
    }


class TestNotifications(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password")
        self.api.token = "fake_token"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_notifications_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": [
                {
                    "id": 1,
                    "iddevice": 100,
                    "icon": "icon",
                    "bezeichnung": "Alert",
                    "meldungtyp": 1,
                    "dateunix": 1234567890,
                    "lat": 1.23,
                    "lng": 4.56,
                    "isread": 0,
                    "radiusin": 0,
                    "radiusout": 0,
                    "zuendon": 0,
                    "zuendoff": 0,
                    "push": 1,
                    "suppressed": 0
                }
            ],
            "number_of_records": 1
        })
        mock_execute.return_value = mock_response

        notifications = await self.api.get_notifications()

        self.assertEqual(len(notifications), 1)
        self.assertIsInstance(notifications[0], Notification)
        self.assertEqual(notifications[0].id, 1)
        self.assertEqual(notifications[0].iddevice, 100)

        mock_execute.assert_called_once()
        args, kwargs = mock_execute.call_args
        self.assertEqual(args[0], "GET")
        self.assertIn("api/v1/notifications", args[1])

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_device_notifications_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": [
                {
                    "id": 2,
                    "iddevice": 101,
                    "icon": "icon",
                    "bezeichnung": "Alert",
                    "meldungtyp": 1,
                    "dateunix": 1234567890,
                    "lat": 1.23,
                    "lng": 4.56,
                    "isread": 0,
                    "radiusin": 0,
                    "radiusout": 0,
                    "zuendon": 0,
                    "zuendoff": 0,
                    "push": 1,
                    "suppressed": 0
                }
            ],
            "number_of_records": 1
        })
        mock_execute.return_value = mock_response

        notifications = await self.api.get_device_notifications(101)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].id, 2)
        self.assertEqual(notifications[0].iddevice, 101)

        mock_execute.assert_called_once()
        args, kwargs = mock_execute.call_args
        self.assertIn("api/v1/notifications/101", args[1])

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_custom_notifications_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "success": [
                {
                    "id": 3,
                    "iddevice": 102,
                    "icon": "icon",
                    "bezeichnung": "Alert",
                    "meldungtyp": 1,
                    "dateunix": 1234567890,
                    "lat": 1.23,
                    "lng": 4.56,
                    "isread": 0,
                    "radiusin": 0,
                    "radiusout": 0,
                    "zuendon": 0,
                    "zuendoff": 0,
                    "push": 1,
                    "suppressed": 0
                }
            ],
            "number_of_records": 1
        })
        mock_execute.return_value = mock_response

        notifications = await self.api.get_custom_notifications(102, 1234567000, 1234567890)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].id, 3)

        mock_execute.assert_called_once()
        args, kwargs = mock_execute.call_args
        self.assertIn("api/v1/customnotifications/102", args[1])
        self.assertEqual(kwargs["params"]["startDate"], 1234567000)
        self.assertEqual(kwargs["params"]["endDate"], 1234567890)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_mark_notifications_read_by_device_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"success": 5})
        mock_execute.return_value = mock_response

        result = await self.api.mark_notifications_read_by_device(103, 1)

        self.assertEqual(result, 5)
        mock_execute.assert_called_once()
        args, kwargs = mock_execute.call_args
        self.assertEqual(args[0], "PUT")
        self.assertIn("api/v1/notifications/markReadByDevice/103", args[1])
        self.assertEqual(kwargs["params"]["isRead"], 1)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_mark_notifications_read_by_customer_success(self, mock_execute):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"success": "Notifications updated"})
        mock_execute.return_value = mock_response

        result = await self.api.mark_notifications_read_by_customer(1)

        self.assertEqual(result, "Notifications updated")
        mock_execute.assert_called_once()
        args, kwargs = mock_execute.call_args
        self.assertEqual(args[0], "PUT")
        self.assertIn("api/v1/notifications/markReadByCustomer", args[1])
        self.assertEqual(kwargs["params"]["isRead"], 1)


class TestGetNotificationsOptionalParams(unittest.IsolatedAsyncioTestCase):
    """Cover the optional alert_type, is_read, and count branches in notification endpoints."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password")
        self.api.token = "fake_token"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_notifications_with_alert_type_enum(self, mock_execute):
        """get_notifications with an AlertType enum hits the alert_type branch."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value=_notification_payload()))
        result = await self.api.get_notifications(alert_type=AlertType.SOS)
        self.assertEqual(len(result), 1)
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["alertType"], int(AlertType.SOS))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_notifications_with_is_read(self, mock_execute):
        """get_notifications with is_read hits the is_read branch."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value=_notification_payload()))
        result = await self.api.get_notifications(is_read=0)
        self.assertEqual(len(result), 1)
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["isRead"], 0)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_device_notifications_with_alert_type_enum(self, mock_execute):
        """get_device_notifications with an AlertType enum hits the alert_type branch."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value=_notification_payload()))
        result = await self.api.get_device_notifications(10, alert_type=AlertType.SOS)
        self.assertEqual(len(result), 1)
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["alertType"], int(AlertType.SOS))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_device_notifications_with_is_read(self, mock_execute):
        """get_device_notifications with is_read hits the is_read branch."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value=_notification_payload()))
        result = await self.api.get_device_notifications(10, is_read=1)
        self.assertEqual(len(result), 1)
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["isRead"], 1)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_custom_notifications_with_alert_type_enum(self, mock_execute):
        """get_custom_notifications with an AlertType enum hits the alert_type branch."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value=_notification_payload()))
        result = await self.api.get_custom_notifications(10, 1000, 2000, alert_type=AlertType.SOS)
        self.assertEqual(len(result), 1)
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["alertType"], int(AlertType.SOS))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_custom_notifications_with_count(self, mock_execute):
        """get_custom_notifications with count hits the count branch."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value=_notification_payload()))
        result = await self.api.get_custom_notifications(10, 1000, 2000, count=25)
        self.assertEqual(len(result), 1)
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["noOfNotification"], 25)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_get_custom_notifications_with_is_read(self, mock_execute):
        """get_custom_notifications with is_read hits the is_read branch."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value=_notification_payload()))
        result = await self.api.get_custom_notifications(10, 1000, 2000, is_read=0)
        self.assertEqual(len(result), 1)
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["isRead"], 0)


class TestMarkNotificationsReadEnumParam(unittest.IsolatedAsyncioTestCase):
    """Tests for mark_notifications_read_by_device/customer with AlertType enum."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password")
        self.api.token = "fake_token"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_mark_read_by_device_with_alert_type_enum(self, mock_execute):
        """mark_notifications_read_by_device with an AlertType enum passes the int value."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value={"success": 3}))
        result = await self.api.mark_notifications_read_by_device(1, 1, alert_type=AlertType.SOS)
        self.assertEqual(result, 3)
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["alertType"], int(AlertType.SOS))

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_mark_read_by_customer_with_alert_type_enum(self, mock_execute):
        """mark_notifications_read_by_customer with an AlertType enum passes the int value."""
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value={"success": "updated"}))
        result = await self.api.mark_notifications_read_by_customer(1, alert_type=AlertType.SOS)
        self.assertEqual(result, "updated")
        _, kwargs = mock_execute.call_args
        self.assertEqual(kwargs["params"]["alertType"], int(AlertType.SOS))


class TestGetCustomNotificationsUnexpectedResponse(unittest.IsolatedAsyncioTestCase):
    """get_custom_notifications must return List[Notification] or raise PajGpsApiError."""

    def setUp(self):
        self.api = PajGpsApi("test@example.com", "password")
        self.api.token = "fake_token"

    async def asyncTearDown(self):
        await self.api.close()

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_missing_success_key_raises(self, mock_execute):
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value={"error": "bad"}))
        with self.assertRaises(Exception):
            await self.api.get_custom_notifications(1, 1000, 2000)

    @patch("pajgps_api.pajgps_requests.PajGpsRequests._execute_request")
    async def test_success_is_not_a_list_raises(self, mock_execute):
        mock_execute.return_value = AsyncMock(json=AsyncMock(return_value={"success": "unexpected_string"}))
        with self.assertRaises(Exception):
            await self.api.get_custom_notifications(1, 1000, 2000)


if __name__ == '__main__':
    unittest.main()
