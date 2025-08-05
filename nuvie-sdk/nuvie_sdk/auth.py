"""
This module handles authentication-related functionalities such as creating JWT
tokens, setting cookies, and verifying passwords.
"""

from typing import Any
from datetime import datetime, timedelta

import jwt

from fastapi import Response
from passlib.context import CryptContext

import constants as c

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Creates a JWT access token with an expiration time."""

    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, c.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def set_token_cookie(response: Response, token: str):
    """Sets the JWT token in the response cookies."""

    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=False,
        samesite="none",
        max_age=7200,  # In seconds
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt."""

    return pwd_context.hash(password)
