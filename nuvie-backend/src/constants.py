import os

from multiprocessing import cpu_count

import dotenv


# * ###########################################################################
# * Environment variables
# * ###########################################################################

# Loading ".env" file
dotenv.load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "Nuvie")

SECRET_KEY = os.getenv("SECRET_KEY", None)
if SECRET_KEY is None:
    raise ValueError("Environment variable SECRET_KEY is not set!")

# Must be "0.0.0.0" if running in a Docker container
HOST = os.environ.get("HOST", "0.0.0.0")
try:
    PORT = int(os.environ.get("PORT", 8000))
except ValueError:
    raise ValueError("Environment variable PORT must be a valid integer")

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
# * First super user credentials
# * ###########################################################################

FIRST_SUPERUSER_EMAIL = os.getenv(
    "FIRST_SUPERUSER_EMAIL", "vinicius7427@gmail.com"
)
FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "12345678")
FIRST_SUPERUSER_FULL_NAME = os.getenv(
    "FIRST_SUPERUSER_FULL_NAME", "Vinícius H. A. Praxedes"
)


# * ###########################################################################
# * Other server configurations
# * ###########################################################################

API_V1_STR = "/api/v1"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours
