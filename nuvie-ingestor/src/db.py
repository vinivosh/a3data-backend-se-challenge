from sqlmodel import Session, create_engine

from logger import log
import constants as c

from nuvie_sdk.models import *


engine = create_engine(str(c.get_postgres_uri()))


# make sure all SQLModel models are imported (nuvie_sdk.models) before
# initializing DB otherwise, SQLModel might fail to initialize relationships
# properly for more details:
#
# https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    log.info("Initializing database...")
    pass
    log.info("Database initialized successfully!")
