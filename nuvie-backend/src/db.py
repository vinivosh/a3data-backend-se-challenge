from sqlmodel import Session, create_engine, select

from src.logger import log
import src.constants as c

from nuvie_sdk.models import User, UserCreate


engine = create_engine(str(c.get_postgres_uri()))


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

        # TODO: Implement user creation

        log.info("First superuser created with success!")
