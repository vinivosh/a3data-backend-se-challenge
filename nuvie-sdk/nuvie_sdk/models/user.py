"""Contains user-related models."""

from sqlmodel import Field, SQLModel
from sqlalchemy.sql import false
from pydantic import EmailStr

# from datetime import datetime

from .. import constants as c


class UserBase(SQLModel):
    """Base model for User."""

    email: EmailStr = Field(unique=True, index=True, max_length=512)
    full_name: str = Field(nullable=False, default=None, max_length=1024)


class UserSignup(UserBase):
    """Properties to receive via API on signup."""

    password: str = Field(min_length=8, max_length=128)


class UserCreate(UserBase):
    """Properties to receive via API on user creation (done by a superuser)."""

    password: str = Field(min_length=8, max_length=128)
    is_superuser: bool = False


class UserUpdate(SQLModel):
    """Properties to receive via API on User update, all optional."""

    email: EmailStr | None = Field(default=None, max_length=512)
    full_name: str | None = Field(default=None, max_length=1024)


class UpdatePassword(SQLModel):
    """Properties to receive via API on updating the password."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    """Properties to return via API, ID always required."""

    id: int
    is_superuser: bool = False


class UsersPublic(SQLModel):
    """Properties to return via API, for multiple users."""

    data: list[UserPublic]
    count: int


class User(UserBase, table=True):
    """
    Database model for User table.

    Tables and fields are created, deleted or modified with Alembic migrations
    generated based on this class.
    """

    __tablename__ = c.USER_TABLE_NAME  # type: ignore
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    is_superuser: bool = Field(
        nullable=False,
        default=False,
        sa_column_kwargs={"server_default": false()},
    )
    hashed_password: str
