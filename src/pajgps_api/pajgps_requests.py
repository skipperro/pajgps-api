import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Set

import aiohttp

from .pajgps_api_error import AuthenticationError, TokenRefreshError, RequestError
from .models.auth import AuthResponse


class PajGpsRequests(ABC):
    """Low-level async HTTP client with retry, timeout, and token management."""

    DEFAULT_BASE_URL: str = "https://connect.paj-gps.de/"

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 5,
        max_retries: int = 3,
        base_url: Optional[str] = None,
    ) -> None:
        self.email: Optional[str] = email
        self.password: Optional[str] = password
        self._session: Optional[aiohttp.ClientSession] = None
        self.base_url: str = base_url or self.DEFAULT_BASE_URL
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[int] = None
        # Retry/timeout configuration
        self.timeout: int = timeout  # base timeout in seconds (first attempt)
        self.max_retries: int = max_retries  # total number of attempts
        # HTTP status codes that should trigger a retry
        self._retry_statuses: Set[int] = {500, 502, 503, 504, 429}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp client session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> "PajGpsRequests":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers: Dict[str, str] = {
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @abstractmethod
    async def login(self, email: Optional[str] = None, password: Optional[str] = None) -> AuthResponse:
        """Log in to the API and get a token."""
        pass

    @abstractmethod
    async def update_token(self) -> AuthResponse:
        """Refresh the access token using the refresh token."""
        pass

    async def _execute_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        refresh_on_401: bool = True,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        """
        Execute an async HTTP request with retry and incremental timeout logic.
        - First attempt uses `self.timeout` seconds, each next attempt adds `self.timeout` seconds.
        - Retries are performed on network timeouts/connection errors and on HTTP statuses in `self._retry_statuses`.
        - 401 is handled specially by attempting a token refresh once within the same attempt (if `refresh_on_401` is True).
        Returns: aiohttp.ClientResponse
        Raises: RequestError on final failure
        """
        headers = headers or {}
        # Pop timeout from kwargs if present to avoid multiple values
        timeout_override: Optional[int] = kwargs.pop("timeout", None)

        last_exception: Optional[Exception] = None
        session = await self._get_session()

        for attempt in range(1, self.max_retries + 1):
            current_timeout = aiohttp.ClientTimeout(total=timeout_override or (self.timeout * attempt))
            try:
                resp = await session.request(method, url, headers=headers, timeout=current_timeout, **kwargs)

                # Handle 401 with a one-time token refresh and immediate retry (same attempt)
                if resp.status == 401 and refresh_on_401:
                    try:
                        if self.refresh_token:
                            try:
                                await self.update_token()
                            except TokenRefreshError:
                                if self.email and self.password:
                                    await self.login()
                                else:
                                    raise
                        elif self.email and self.password:
                            await self.login()
                        else:
                            raise AuthenticationError("Not authenticated. Please call login() first.")
                        headers.update(self._get_headers())
                        resp = await session.request(method, url, headers=headers, timeout=current_timeout, **kwargs)
                    except (TokenRefreshError, AuthenticationError):
                        # Leave resp as is; will error below
                        pass

                # Retry on specific HTTP status codes
                if resp.status in self._retry_statuses:
                    if attempt == self.max_retries:
                        resp.raise_for_status()
                    else:
                        continue

                # For other statuses, raise if error or return
                resp.raise_for_status()
                return resp

            except (asyncio.TimeoutError, aiohttp.ClientConnectionError) as e:
                last_exception = e
                if attempt == self.max_retries:
                    raise e
                continue

        # If the loop exits without a return, raise the last exception or generic error
        if last_exception:
            raise last_exception
        raise aiohttp.ClientError("Request failed after retries")

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Internal method to handle async API requests."""
        if not self.token:
            if self.email and self.password:
                await self.login()
            else:
                raise AuthenticationError("Not authenticated. Please call login() first.")

        url: str = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers: Dict[str, str] = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        try:
            response = await self._execute_request(method, url, headers=headers, **kwargs)
            return await response.json()
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                raise AuthenticationError("Unauthorized. Please login.")
            raise RequestError(f"API request failed: {str(e)}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise RequestError(f"Request failed: {str(e)}")
