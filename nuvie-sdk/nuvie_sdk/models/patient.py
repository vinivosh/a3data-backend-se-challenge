"""Contains patient-related models."""

from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from .. import constants as c


class MaritalStatus(str, Enum):
    """Marital status options."""

    MARRIED = "married"
    SINGLE = "single"
    NONE = "none"


class Race(str, Enum):
    """Race options."""

    WHITE = "white"
    BLACK = "black"
    ASIAN = "asian"


class Ethnicity(str, Enum):
    """Ethnicity options."""

    HISPANIC = "hispanic"
    NONHISPANIC = "nonhispanic"


class Gender(str, Enum):
    """Gender options."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class PatientBase(SQLModel):
    """Base model for Patient."""

    birthdate: date = Field(nullable=False)
    deathdate: date | None = Field(default=None, nullable=True)
    ssn: str = Field(nullable=False, max_length=32)
    drivers_license: str | None = Field(
        default=None, nullable=True, max_length=64
    )
    passport: str | None = Field(default=None, nullable=True, max_length=16)
    prefix: str | None = Field(default=None, nullable=True, max_length=16)
    first: str = Field(nullable=False, max_length=128)
    last: str = Field(nullable=False, max_length=128)
    suffix: str | None = Field(default=None, nullable=True, max_length=16)
    maiden: str | None = Field(default=None, nullable=True, max_length=128)
    marital: MaritalStatus | None = Field(default=None, nullable=True)
    race: Race = Field(nullable=False)
    ethnicity: Ethnicity = Field(nullable=False)
    gender: Gender = Field(nullable=False)
    birthplace: str = Field(nullable=False, max_length=128)
    address: str = Field(nullable=False, max_length=256)
    city: str = Field(nullable=False, max_length=64)
    state: str = Field(nullable=False, max_length=64)
    county: str = Field(nullable=False, max_length=64)
    zip: str | None = Field(default=None, nullable=True, max_length=16)
    lat: Decimal = Field(nullable=False, decimal_places=4, max_digits=12)
    lon: Decimal = Field(nullable=False, decimal_places=4, max_digits=12)
    healthcare_expenses: Decimal = Field(
        nullable=False, decimal_places=2, max_digits=12
    )
    healthcare_coverage: Decimal = Field(
        nullable=False, decimal_places=2, max_digits=12
    )


class PatientCreate(PatientBase):
    """Properties to receive via API on patient creation."""

    id: UUID | None = Field(default_factory=uuid4, nullable=False)


class PatientUpdate(SQLModel):
    """Properties to receive via API on Patient update, all optional."""

    birthdate: date | None = Field(default=None)
    deathdate: date | None = Field(default=None)
    ssn: str | None = Field(default=None, max_length=32)
    drivers_license: str | None = Field(default=None, max_length=64)
    passport: str | None = Field(default=None, max_length=16)
    prefix: str | None = Field(default=None, max_length=16)
    first: str | None = Field(default=None, max_length=128)
    last: str | None = Field(default=None, max_length=128)
    suffix: str | None = Field(default=None, max_length=16)
    maiden: str | None = Field(default=None, max_length=128)
    marital: MaritalStatus | None = Field(default=None)
    race: Race | None = Field(default=None)
    ethnicity: Ethnicity | None = Field(default=None)
    gender: Gender | None = Field(default=None)
    birthplace: str | None = Field(default=None, max_length=128)
    address: str | None = Field(default=None, max_length=256)
    city: str | None = Field(default=None, max_length=64)
    state: str | None = Field(default=None, max_length=64)
    county: str | None = Field(default=None, max_length=64)
    zip: str | None = Field(default=None, max_length=16)
    lat: Decimal | None = Field(default=None, decimal_places=4, max_digits=12)
    lon: Decimal | None = Field(default=None, decimal_places=4, max_digits=12)
    healthcare_expenses: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=12
    )
    healthcare_coverage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=12
    )


class PatientPublic(PatientBase):
    """Properties to return via API, ID always required."""

    id: UUID


class PatientsPublic(SQLModel):
    """Properties to return via API, for multiple patients."""

    data: list[PatientPublic]
    count: int


class Patient(PatientBase, table=True):
    """
    Database model for Patient table.

    Tables and fields are created, deleted or modified with Alembic migrations
    generated based on this class.
    """

    __tablename__ = c.PATIENT_TABLE_NAME  # type: ignore
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
