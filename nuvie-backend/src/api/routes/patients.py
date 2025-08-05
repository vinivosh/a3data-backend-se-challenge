from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from api.deps import CurrentUser, SessionDep
from nuvie_sdk.models import (
    Message,
    PatientCreate,
    PatientPublic,
    PatientsPublic,
    PatientUpdate,
)
from nuvie_sdk.use_cases import patient_use_case


router = APIRouter()


@router.get(
    "/",
    response_model=PatientsPublic,
)
def read_patients(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve patients."""

    count = patient_use_case.count_patients(session=session)
    patients = patient_use_case.get_patients(
        session=session, skip=skip, limit=limit
    )

    # Convert Patient models to PatientPublic
    patients = [PatientPublic.model_validate(patient) for patient in patients]
    return PatientsPublic(data=patients, count=count)


@router.post(
    "/",
    response_model=PatientPublic,
)
def create_patient(
    *,
    session: SessionDep,
    patient_in: PatientCreate,
    current_user: CurrentUser,
) -> Any:
    """Create new patient."""

    # Check if patient with this SSN already exists
    existing_patient = patient_use_case.get_patient_by_ssn(
        session=session, ssn=patient_in.ssn
    )
    if existing_patient:
        raise HTTPException(
            status_code=400,
            detail="A patient with this SSN already exists in the system.",
        )

    # Check if patient with this ID already exists, if needed
    if patient_in.id and patient_use_case.get_patient_by_id(
        session=session, patient_id=patient_in.id
    ):
        raise HTTPException(
            status_code=400,
            detail="A patient with this ID already exists in the system.",
        )

    patient = patient_use_case.create_patient(
        session=session, patient_create=patient_in
    )

    return patient


@router.get("/{patient_id}", response_model=PatientPublic)
def read_patient_by_id(
    patient_id: UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """Get a specific patient by id."""

    patient = patient_use_case.get_patient_by_id(
        session=session, patient_id=patient_id
    )
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="The patient with this id does not exist in the system",
        )
    return patient


@router.patch("/{patient_id}", response_model=PatientPublic)
def update_patient(
    *,
    session: SessionDep,
    patient_id: UUID,
    patient_in: PatientUpdate,
    current_user: CurrentUser,
) -> Any:
    """Update a patient."""

    db_patient = patient_use_case.get_patient_by_id(
        session=session, patient_id=patient_id
    )
    if not db_patient:
        raise HTTPException(
            status_code=404,
            detail="The patient with this id does not exist in the system",
        )

    # Check if SSN is being updated and if it conflicts with existing patient
    if patient_in.ssn:
        existing_patient = patient_use_case.get_patient_by_ssn(
            session=session, ssn=patient_in.ssn
        )
        if existing_patient and existing_patient.id != patient_id:
            raise HTTPException(
                status_code=409, detail="Patient with this SSN already exists"
            )

    db_patient = patient_use_case.update_patient(
        session=session, db_patient=db_patient, patient_in=patient_in
    )
    return db_patient


@router.delete("/{patient_id}", response_model=Message)
def delete_patient(
    session: SessionDep, current_user: CurrentUser, patient_id: UUID
) -> Any:
    """Delete a patient."""

    # Check if patient exists
    patient = patient_use_case.get_patient_by_id(
        session=session, patient_id=patient_id
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Delete the patient
    success = patient_use_case.delete_patient(
        session=session, patient_id=patient_id
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete patient")

    return Message(message="Patient deleted successfully")


@router.get("/search/ssn/{ssn}", response_model=PatientPublic)
def read_patient_by_ssn(
    ssn: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """Get a specific patient by SSN."""

    patient = patient_use_case.get_patient_by_ssn(session=session, ssn=ssn)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="The patient with this SSN does not exist in the system",
        )
    return patient
