import requests
from .http_client import HttpClient
from .exceptions import AuthenticationError, TokenRefreshError


class PajGpsApi(HttpClient):
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
                return data["success"]
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
                return data["success"]
            else:
                raise TokenRefreshError(f"Token refresh failed: {data.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise TokenRefreshError(f"Request failed: {str(e)}")

    # ── Device endpoints ──────────────────────────────────────────────

    def get_devices(self):
        """Get data for all devices the user has permission to view."""
        data = self._request("GET", "api/v1/device")
        return data.get("success", data)

    def get_device(self, device_id):
        """Get data for a single device by its ID."""
        data = self._request("GET", f"api/v1/device/{device_id}")
        return data.get("success", data)

    def update_device(self, device_id, **kwargs):
        """Update a device by its ID. Pass device fields as keyword arguments."""
        data = self._request("PUT", f"api/v1/device/{device_id}", json=kwargs)
        return data.get("success", data)
