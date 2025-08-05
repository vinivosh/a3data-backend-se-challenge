"""This file contains the models used in the Nuvie SDK."""

from .user import *

from sqlmodel import Field, SQLModel


class Message(SQLModel):
    """A simple message model for API responses."""

    message: str


class Token(SQLModel):
    """JSON payload containing access token."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Contents of JWT token."""

    sub: int | None = None


class NewPassword(SQLModel):
    """Model for changing a user's password."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)
