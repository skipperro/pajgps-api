from .base import BaseModel


class AuthResponse(BaseModel):
    """Model representing an authentication response."""

    token = None
    refresh_token = None
    userID = None
    routeIcon = None
