import unittest
from unittest.mock import patch, AsyncMock
from pajgps_api import PajGpsApi
from pajgps_api.models import Notification


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
