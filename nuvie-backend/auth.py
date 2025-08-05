from typing import Any
from datetime import datetime, timedelta

import jwt

from fastapi import Response
from passlib.context import CryptContext

import src.constants as c

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, c.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def set_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=False,
        samesite="None",
        max_age=7200,  # In seconds
    )
