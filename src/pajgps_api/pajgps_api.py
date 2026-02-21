import requests
from .pajgps_requests import PajGpsRequests
from .pajgps_api_error import AuthenticationError, TokenRefreshError
from .models import Device, TrackPoint, SensorData, AuthResponse


class PajGpsApi(PajGpsRequests):
    """Class to handle communication with the PAJ GPS API."""

    # ── Authentication endpoints ──────────────────────────────────────

    def login(self, email=None, password=None):
        """Log in to the API and get a token."""
        email = email or self.email
        password = password or self.password

        if not email or not password:
            raise AuthenticationError("Email and password are required for login.")

        params = {
            "email": email,
            "password": password
        }
        
        url = f"{self.base_url.rstrip('/')}/api/v1/login"
        try:
            response = self._execute_request("POST", url, params=params, refresh_on_401=False)
            data = response.json()
            
            if "success" in data:
                self.token = data["success"]["token"]
                self.refresh_token = data["success"]["refresh_token"]
                self.user_id = data["success"]["userID"]
                self.email = email
                self.password = password
                return AuthResponse(**data["success"])
            else:
                raise AuthenticationError(f"Login failed: {data.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Request failed: {str(e)}")

    def update_token(self):
        """Refresh the access token using the refresh token."""
        if not self.email or not self.refresh_token:
            raise TokenRefreshError("Email and refresh token are required to refresh the token.")

        params = {
            "email": self.email,
            "refresh_token": self.refresh_token
        }
        
        url = f"{self.base_url.rstrip('/')}/api/v1/updatetoken"
        try:
            response = self._execute_request("POST", url, params=params, refresh_on_401=False)
            data = response.json()
            
            if "success" in data:
                self.token = data["success"]["token"]
                self.refresh_token = data["success"]["refresh_token"]
                return AuthResponse(**data["success"])
            else:
                raise TokenRefreshError(f"Token refresh failed: {data.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise TokenRefreshError(f"Request failed: {str(e)}")

    # ── Device endpoints ──────────────────────────────────────────────

    def get_devices(self):
        """Get data for all devices the user has permission to view."""
        data = self._request("GET", "api/v1/device")
        if "success" in data:
            success_data = data["success"]
            if isinstance(success_data, list):
                return [Device(**item) for item in success_data]
            return success_data
        return data

    def get_device(self, device_id):
        """Get data for a single device by its ID."""
        data = self._request("GET", f"api/v1/device/{device_id}")
        if "success" in data:
            success_data = data["success"]
            if isinstance(success_data, dict):
                return Device(**success_data)
            return success_data
        return data

    def update_device(self, device_id, **kwargs):
        """Update a device by its ID. Pass device fields as keyword arguments."""
        data = self._request("PUT", f"api/v1/device/{device_id}", json=kwargs)
        if "success" in data:
            success_data = data["success"]
            if isinstance(success_data, dict):
                return Device(**success_data)
            return success_data
        return data

    # ── Tracking Data endpoints ───────────────────────────────────────

    def get_tracking_data_last_minutes(self, device_id, last_minutes, gps=None, wifi=None, sort=None):
        """Get device tracking data based on last minutes.

        Args:
            device_id: The device ID.
            last_minutes: Number of last minutes to retrieve data for.
            gps: Optional. 0 or 1 to include GPS points.
            wifi: Optional. 0 or 1 to include Wi-Fi points.
            sort: Optional. Sort order based on id (default descending).
        """
        params = {"lastMinutes": last_minutes}
        if gps is not None:
            params["gps"] = gps
        if wifi is not None:
            params["wifi"] = wifi
        if sort is not None:
            params["sort"] = sort
        data = self._request("GET", f"api/v1/trackerdata/{device_id}/last_minutes", params=params)
        if "success" in data:
            success_data = data["success"]
            if isinstance(success_data, list):
                return [TrackPoint(**item) for item in success_data]
            return success_data
        return data

    def get_tracking_data_last_points(self, device_id, last_points, gps=None, wifi=None, sort=None):
        """Get device tracking data based on last points.

        Args:
            device_id: The device ID.
            last_points: Number of last points to retrieve.
            gps: Optional. 0 or 1 to include GPS points.
            wifi: Optional. 0 or 1 to include Wi-Fi points.
            sort: Optional. Sort order based on id (default descending).
        """
        params = {"lastPoints": last_points}
        if gps is not None:
            params["gps"] = gps
        if wifi is not None:
            params["wifi"] = wifi
        if sort is not None:
            params["sort"] = sort
        data = self._request("GET", f"api/v1/trackerdata/{device_id}/last_points", params=params)
        if "success" in data:
            success_data = data["success"]
            if isinstance(success_data, list):
                return [TrackPoint(**item) for item in success_data]
            return success_data
        return data

    def get_tracking_data_date_range(self, device_id, date_start, date_end, gps=None, wifi=None, sort=None):
        """Get device tracking data based on a date range.

        Args:
            device_id: The device ID.
            date_start: Start date as a unix timestamp.
            date_end: End date as a unix timestamp.
            gps: Optional. 0 or 1 to include GPS points.
            wifi: Optional. 0 or 1 to include Wi-Fi points.
            sort: Optional. Sort order based on id (default descending).
        """
        params = {"dateStart": date_start, "dateEnd": date_end}
        if gps is not None:
            params["gps"] = gps
        if wifi is not None:
            params["wifi"] = wifi
        if sort is not None:
            params["sort"] = sort
        data = self._request("GET", f"api/v1/trackerdata/{device_id}/date_range", params=params)
        if "success" in data:
            success_data = data["success"]
            if isinstance(success_data, list):
                return [TrackPoint(**item) for item in success_data]
            return success_data
        return data

    def get_all_last_positions(self, device_ids, from_last_point=False):
        """Get all last positions for the given devices.

        Args:
            device_ids: List of device IDs (integers).
            from_last_point: If True, returns all points from the last known dateunix.
        """
        body = {"deviceIDs": device_ids, "fromLastPoint": from_last_point}
        data = self._request("POST", "api/v1/trackerdata/getalllastpositions", json=body)
        if "success" in data:
            success_data = data["success"]
            if isinstance(success_data, list):
                return [TrackPoint(**item) for item in success_data]
            return success_data
        return data

    def get_last_sensor_data(self, device_id):
        """Get last sensor (voltage) data for a device.

        Args:
            device_id: The device ID.
        """
        data = self._request("GET", f"api/v1/sensordata/last/{device_id}")
        if "success" in data:
            success_data = data["success"]
            if isinstance(success_data, dict):
                return SensorData(**success_data)
            return success_data
        return data
