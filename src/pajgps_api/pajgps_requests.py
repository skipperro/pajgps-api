from abc import ABC, abstractmethod
import requests
from .pajgps_api_error import AuthenticationError, TokenRefreshError, RequestError


class PajGpsRequests(ABC):
    """Low-level HTTP client with retry, timeout, and token management."""

    def __init__(self, email=None, password=None, timeout=5, max_retries=3):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://connect.paj-gps.de/"
        self.token = None
        self.refresh_token = None
        self.user_id = None
        # Retry/timeout configuration
        self.timeout = timeout  # base timeout in seconds (first attempt)
        self.max_retries = max_retries  # total number of attempts
        # HTTP status codes that should trigger a retry
        self._retry_statuses = {500, 502, 503, 504, 429}

    def _get_headers(self):
        """Get headers for API requests."""
        headers = {
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @abstractmethod
    def login(self, email=None, password=None):
        """Log in to the API and get a token."""
        pass

    @abstractmethod
    def update_token(self):
        """Refresh the access token using the refresh token."""
        pass

    def _execute_request(self, method, url, headers=None, refresh_on_401=True, **kwargs):
        """
        Execute an HTTP request with retry and incremental timeout logic.
        - First attempt uses `self.timeout` seconds, each next attempt adds `self.timeout` seconds.
        - Retries are performed on network timeouts/connection errors and on HTTP statuses in `self._retry_statuses`.
        - 401 is handled specially by attempting a token refresh once within the same attempt (if `refresh_on_401` is True).
        Returns: requests.Response
        Raises: requests.exceptions.RequestException on final failure
        """
        headers = headers or {}
        # Pop timeout from kwargs if present to avoid multiple values for argument in self.session.request
        timeout_override = kwargs.pop("timeout", None)

        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            current_timeout = timeout_override or (self.timeout * attempt)
            try:
                resp = self.session.request(method, url, headers=headers, timeout=current_timeout, **kwargs)

                # Handle 401 with a one-time token refresh and immediate retry (same attempt)
                if resp.status_code == 401 and refresh_on_401:
                    try:
                        if self.refresh_token:
                            try:
                                self.update_token()
                            except TokenRefreshError:
                                if self.email and self.password:
                                    self.login()
                                else:
                                    raise
                        elif self.email and self.password:
                            self.login()
                        else:
                            raise AuthenticationError("Not authenticated. Please call login() first.")
                        headers.update(self._get_headers())
                        resp = self.session.request(method, url, headers=headers, timeout=current_timeout, **kwargs)
                    except (TokenRefreshError, AuthenticationError):
                        # Leave resp as is; will error below
                        pass

                # Retry on specific HTTP status codes
                if resp.status_code in self._retry_statuses:
                    if attempt == self.max_retries:
                        resp.raise_for_status()
                    else:
                        continue

                # For other statuses, raise if error or return
                resp.raise_for_status()
                return resp

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                if attempt == self.max_retries:
                    raise e
                continue

        # If the loop exits without a return, raise the last exception or generic error
        if last_exception:
            raise last_exception
        # Fallback (shouldn't happen): raise HTTPError
        raise requests.exceptions.RequestException("Request failed after retries")

    def _request(self, method, endpoint, **kwargs):
        """Internal method to handle API requests."""
        if not self.token:
            if self.email and self.password:
                self.login()
            else:
                raise AuthenticationError("Not authenticated. Please call login() first.")

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        try:
            response = self._execute_request(method, url, headers=headers, **kwargs)
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise AuthenticationError("Unauthorized. Please login.")
            raise RequestError(f"API request failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise RequestError(f"Request failed: {str(e)}")
