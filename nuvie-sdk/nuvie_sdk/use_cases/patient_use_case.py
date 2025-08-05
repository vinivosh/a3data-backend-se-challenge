"""Implementation of patient-related use cases (CRUD)."""

from typing import Any
from uuid import UUID

from sqlmodel import Session, select, func

from ..models import (
    Patient,
    PatientCreate,
    PatientUpdate,
)


def create_patient(
    *, session: Session, patient_create: PatientCreate
) -> Patient:
    """Create a new patient."""

    db_obj = Patient.model_validate(patient_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_patient_by_id(*, session: Session, patient_id: UUID) -> Patient | None:
    """Get a patient by ID."""

    statement = select(Patient).where(Patient.id == patient_id)
    patient = session.exec(statement).first()
    return patient


def get_patient_by_ssn(*, session: Session, ssn: str) -> Patient | None:
    """Get a patient by SSN."""

    statement = select(Patient).where(Patient.ssn == ssn)
    patient = session.exec(statement).first()
    return patient


def get_patients(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Patient]:
    """Get multiple patients with pagination."""

    statement = select(Patient).offset(skip).limit(limit)
    patients = session.exec(statement).all()
    return list(patients)


def update_patient(
    *, session: Session, db_patient: Patient, patient_in: PatientUpdate
) -> Any:
    """Update an existing patient."""

    patient_data = patient_in.model_dump(exclude_unset=True)
    db_patient.sqlmodel_update(patient_data)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


def delete_patient(*, session: Session, patient_id: UUID) -> bool:
    """Delete a patient by ID."""

    statement = select(Patient).where(Patient.id == patient_id)
    patient = session.exec(statement).first()
    if patient:
        session.delete(patient)
        session.commit()
        return True
    return False


def count_patients(*, session: Session) -> int:
    """Count total number of patients."""

    statement = select(func.count()).select_from(Patient)
    count = session.exec(statement).one()

    return count
