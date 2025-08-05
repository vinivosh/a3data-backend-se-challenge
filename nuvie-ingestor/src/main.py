import argparse
import csv
import sys

from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import UUID

import zipfile
import httpx
from sqlmodel import Session

from db import engine
from logger import log
from nuvie_sdk.models.patient import (
    PatientCreate,
    Race,
    Ethnicity,
    Gender,
    MaritalStatus,
)
from nuvie_sdk.use_cases import patient_use_case

import constants as c


def download_dataset(url: str, download_dir: Path, zip_filename: str) -> bool:
    """
    Download and extract dataset from URL if not already present.

    Args:
        url: URL to download the dataset from
        download_dir: Directory to save the dataset
        zip_filename: Name of the zip file

    Returns:
        bool: True if download/extraction was successful or already exists
    """

    download_dir.mkdir(parents=True, exist_ok=True)
    zip_path = download_dir / zip_filename

    # Check if already downloaded and extracted
    patients_csv = download_dir / "patients.csv"
    if patients_csv.exists():
        log.info(
            "Dataset already exists, skipping download", path=str(patients_csv)
        )
        return True

    # Check if zip exists but not extracted
    if zip_path.exists():
        log.info("Zip file exists, extracting", path=str(zip_path))
    else:
        log.info("Downloading dataset", url=url, destination=str(zip_path))
        try:
            with httpx.stream("GET", url, timeout=300.0) as response:
                response.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            size_mb = round(zip_path.stat().st_size / 1024 / 1024, 2)
            log.info("Download completed", size_mb=size_mb)
        except Exception as e:
            log.error("Failed to download dataset", error=str(e))
            return False

    # Extract the zip file
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(download_dir)
        log.info("Dataset extracted successfully")

        # Remove the zip file to save space
        zip_path.unlink()
        log.info("Zip file removed to save space")

        return True
    except Exception as e:
        log.error("Failed to extract dataset", error=str(e))
        return False


def parse_csv_row(row: dict[str, str]) -> PatientCreate | None:
    """
    Parse a CSV row into a PatientCreate object.

    Args:
        row: Dictionary representing a CSV row

    Returns:
        PatientCreate object or None if parsing fails
    """

    try:
        # Parse UUID
        patient_id = UUID(row["Id"])

        # Parse dates
        birthdate = datetime.strptime(row["BIRTHDATE"], "%Y-%m-%d").date()
        deathdate = None
        if row["DEATHDATE"].strip():
            deathdate = datetime.strptime(row["DEATHDATE"], "%Y-%m-%d").date()

        # Parse enums with fallback handling
        race_mapping = {
            "white": Race.WHITE,
            "black": Race.BLACK,
            "asian": Race.ASIAN,
        }
        race = race_mapping.get(row["RACE"].lower(), Race.WHITE)

        ethnicity_mapping = {
            "hispanic": Ethnicity.HISPANIC,
            "nonhispanic": Ethnicity.NONHISPANIC,
        }
        ethnicity = ethnicity_mapping.get(
            row["ETHNICITY"].lower(), Ethnicity.NONHISPANIC
        )

        gender_mapping = {
            "M": Gender.MALE,
            "F": Gender.FEMALE,
            "male": Gender.MALE,
            "female": Gender.FEMALE,
        }
        gender = gender_mapping.get(row["GENDER"], Gender.OTHER)

        # Parse marital status
        marital = None
        if row["MARITAL"].strip():
            marital_mapping = {
                "M": MaritalStatus.MARRIED,
                "S": MaritalStatus.SINGLE,
                "married": MaritalStatus.MARRIED,
                "single": MaritalStatus.SINGLE,
            }
            marital = marital_mapping.get(row["MARITAL"], MaritalStatus.NONE)

        # Parse decimal fields with proper rounding for model constraints
        lat = Decimal(str(round(float(row["LAT"]), 4)))
        lon = Decimal(str(round(float(row["LON"]), 4)))
        healthcare_expenses = Decimal(
            str(round(float(row["HEALTHCARE_EXPENSES"]), 2))
        )
        healthcare_coverage = Decimal(
            str(round(float(row["HEALTHCARE_COVERAGE"]), 2))
        )

        patient = PatientCreate(
            id=patient_id,
            birthdate=birthdate,
            deathdate=deathdate,
            ssn=row["SSN"],
            drivers_license=row["DRIVERS"] if row["DRIVERS"].strip() else None,
            passport=row["PASSPORT"] if row["PASSPORT"].strip() else None,
            prefix=row["PREFIX"] if row["PREFIX"].strip() else None,
            first=row["FIRST"],
            last=row["LAST"],
            suffix=row["SUFFIX"] if row["SUFFIX"].strip() else None,
            maiden=row["MAIDEN"] if row["MAIDEN"].strip() else None,
            marital=marital,
            race=race,
            ethnicity=ethnicity,
            gender=gender,
            birthplace=row["BIRTHPLACE"],
            address=row["ADDRESS"],
            city=row["CITY"],
            state=row["STATE"],
            county=row["COUNTY"],
            zip=row["ZIP"] if row["ZIP"].strip() else None,
            lat=lat,
            lon=lon,
            healthcare_expenses=healthcare_expenses,
            healthcare_coverage=healthcare_coverage,
        )

        return patient

    except (ValueError, KeyError, InvalidOperation) as e:
        log.warning(
            "Failed to parse CSV row",
            error=str(e),
            row_id=row.get("Id", "unknown"),
        )
        return None


def process_patient_batch(
    patients_batch: list[PatientCreate],
) -> dict[str, int]:
    """
    Process a batch of patients and insert them into the database.

    Args:
        patients_batch: List of PatientCreate objects

    Returns:
        Dictionary with statistics about the processing
    """

    stats = {"created": 0, "skipped": 0, "errors": 0}

    with Session(engine) as session:
        for patient in patients_batch:
            try:
                # Check if patient already exists by SSN
                existing_patient = patient_use_case.get_patient_by_ssn(
                    session=session, ssn=patient.ssn
                )
                if existing_patient:
                    log.debug(
                        "Patient already exists, skipping", ssn=patient.ssn
                    )
                    stats["skipped"] += 1
                    continue

                # Create new patient
                patient_use_case.create_patient(
                    session=session, patient_create=patient
                )
                stats["created"] += 1
                log.debug(
                    "Patient created successfully", patient_id=str(patient.id)
                )

            except Exception as e:
                log.error(
                    "Failed to create patient",
                    patient_id=str(patient.id),
                    ssn=patient.ssn,
                    error=str(e),
                )
                stats["errors"] += 1

    return stats


def process_patients_file(csv_file_path: Path, workers: int = 4) -> None:
    """
    Process the patients CSV file with multiple workers.

    Args:
        csv_file_path: Path to the patients CSV file
        workers: Number of worker threads to use
    """

    if not csv_file_path.exists():
        log.error("Patients CSV file not found", path=str(csv_file_path))
        return

    log.info(
        "Starting patient processing", file=str(csv_file_path), workers=workers
    )

    # Read and parse CSV file
    patients_data = []
    total_rows = 0
    parse_errors = 0

    with open(csv_file_path, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            total_rows += 1
            patient = parse_csv_row(row)
            if patient:
                patients_data.append(patient)
            else:
                parse_errors += 1

    log.info(
        "CSV parsing completed",
        total_rows=total_rows,
        valid_patients=len(patients_data),
        parse_errors=parse_errors,
    )

    if not patients_data:
        log.error("No valid patients found in CSV file")
        return

    # Split patients into batches for processing
    # 4 batches per worker
    batch_size = max(1, len(patients_data) // (workers * 4))
    batches = [
        patients_data[i : i + batch_size]
        for i in range(0, len(patients_data), batch_size)
    ]

    log.info(
        "Processing patients in batches",
        total_patients=len(patients_data),
        batch_count=len(batches),
        batch_size=batch_size,
    )

    # Process batches with ThreadPoolExecutor
    total_stats = {"created": 0, "skipped": 0, "errors": 0}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all batches
        future_to_batch = {
            executor.submit(process_patient_batch, batch): i
            for i, batch in enumerate(batches)
        }

        # Process completed batches
        for future in as_completed(future_to_batch):
            batch_num = future_to_batch[future]
            try:
                batch_stats = future.result()
                for key in total_stats.keys():
                    total_stats[key] += batch_stats[key]

                log.info(
                    "Batch completed",
                    batch=batch_num,
                    created=batch_stats["created"],
                    skipped=batch_stats["skipped"],
                    errors=batch_stats["errors"],
                )

            except Exception as e:
                log.error(
                    "Batch processing failed", batch=batch_num, error=str(e)
                )
                total_stats["errors"] += len(batches[batch_num])

    # Final statistics
    success_rate = total_stats["created"] / len(patients_data) * 100
    log.info(
        "Patient processing completed",
        total_processed=sum(total_stats.values()),
        created=total_stats["created"],
        skipped=total_stats["skipped"],
        errors=total_stats["errors"],
        success_rate=f"{success_rate:.1f}%",
    )


def main():
    """Main entry point for the ingestor script."""
    parser = argparse.ArgumentParser(
        description=(
            "Nuvie Data Ingestor - Import patient data from external sources"
        )
    )
    parser.add_argument(
        "--dataset",
        choices=["synthea"],
        default="synthea",
        help="Dataset to download and process (default: synthea)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=c.WORKERS,
        help=f"Number of worker threads (default: {c.WORKERS})",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip download step and process existing CSV file",
    )

    args = parser.parse_args()

    log.info(
        "Starting Nuvie Data Ingestor",
        dataset=args.dataset,
        workers=args.workers,
        skip_download=args.skip_download,
    )

    # Setup paths
    base_dir = Path(__file__).parent.parent
    download_dir = base_dir / "~downloads"

    # Dataset configuration
    datasets = {
        "synthea": {
            "url": c.SYNTHEA_URL,
            "zip_filename": c.SYNTHEA_ZIP_NAME,
            "csv_filename": "patients.csv",
        }
    }

    if args.dataset not in datasets:
        log.error("Unsupported dataset", dataset=args.dataset)
        sys.exit(1)

    dataset_config = datasets[args.dataset]

    # Download and extract dataset
    if not args.skip_download:
        success = download_dataset(
            url=dataset_config["url"],
            download_dir=download_dir,
            zip_filename=dataset_config["zip_filename"],
        )
        if not success:
            log.error("Failed to download dataset")
            sys.exit(1)

    # Process patients
    csv_file_path = download_dir / dataset_config["csv_filename"]
    process_patients_file(csv_file_path, workers=args.workers)

    log.info("Ingestor completed successfully")


if __name__ == "__main__":
    main()
