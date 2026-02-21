from typing import Any, Optional

from .base import BaseModel


class AuthResponse(BaseModel):
    """Model representing an authentication response."""

    token: Optional[str] = None
    refresh_token: Optional[str] = None
    userID: Optional[int] = None
    routeIcon: Optional[str] = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
