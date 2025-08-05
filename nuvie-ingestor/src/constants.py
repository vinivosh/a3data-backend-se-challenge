import os

from multiprocessing import cpu_count

import dotenv


# * ###########################################################################
# * Environment variables
# * ###########################################################################

# Loading ".env" file
dotenv.load_dotenv()

WORKERS = os.environ.get("WORKERS", None)
if WORKERS is None:
    WORKERS = cpu_count()
else:
    try:
        WORKERS = int(WORKERS)
    except ValueError:
        raise ValueError(
            "Environment variable WORKERS must be a valid integer"
        )

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


# * ###########################################################################
# * DB credentials
# * ###########################################################################

POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

POSTGRES_DB = os.getenv("POSTGRES_DB", "nuvie")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")


def get_postgres_uri():
    return f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


# * ###########################################################################
# * Dataset URLs
# * ###########################################################################

SYNTHEA_URL = os.getenv(
    "SYNTHEA_URL",
    "https://synthetichealth.github.io/synthea-sample-data/downloads/synthea_sample_data_csv_apr2020.zip",
)
SYNTHEA_ZIP_NAME = os.getenv(
    "SYNTHEA_ZIP_NAME", "synthea_sample_data_csv_nov2021.zip"
)
