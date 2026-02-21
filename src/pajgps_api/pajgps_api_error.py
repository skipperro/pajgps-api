class PajGpsApiError(Exception):
    """Base exception for PajGpsApi."""
    pass

class AuthenticationError(PajGpsApiError):
    """Raised when authentication fails."""
    pass

class TokenRefreshError(PajGpsApiError):
    """Raised when token refresh fails."""
    pass

class RequestError(PajGpsApiError):
    """Raised when an API request fails."""
    pass
