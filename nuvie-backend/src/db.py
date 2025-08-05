from sqlmodel import Session, create_engine, select

from logger import log
import constants as c

from nuvie_sdk.models import User, UserCreate
from nuvie_sdk.use_cases import user_use_case


engine = create_engine(str(c.get_postgres_uri()))


# make sure all SQLModel models are imported (app.models) before initializing
# DB otherwise, SQLModel might fail to initialize relationships properly for
# more details:
#
# https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Creating first superuser if none exists
    user = session.exec(
        select(User).where(User.email == c.FIRST_SUPERUSER_EMAIL)
    ).first()

    if not user:
        log.info("Creating first superuser...")
        new_user = UserCreate(
            email=c.FIRST_SUPERUSER_EMAIL,
            password=c.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name=c.FIRST_SUPERUSER_FULL_NAME,
        )
        log.debug(f"New user data: {new_user}")

        user_use_case.create_user(session=session, user_create=new_user)

        log.info("First superuser created with success!")
