"""Contains constants used throughout Nuvie SDK."""

import os

import dotenv

# Loading ".env" file
dotenv.load_dotenv()

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
    """Returns the PostgreSQL URI for SQLAlchemy."""

    return f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


# * ###########################################################################
# * DB table names
# * ###########################################################################

USER_TABLE_NAME: str = "users"
