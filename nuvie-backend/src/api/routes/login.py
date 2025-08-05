from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

import constants as c
import nuvie_sdk.auth as auth

from api.deps import CurrentUser, SessionDep
from nuvie_sdk.models import Token, UserPublic
from nuvie_sdk.use_cases import user_use_case

router = APIRouter()


@router.post("/access-token")
def login_access_token(
    response: Response,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    user = user_use_case.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    access_token_expires = timedelta(minutes=c.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = auth.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    auth.set_token_cookie(response, access_token)

    return Token(access_token=access_token)


@router.post("/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """Test access token"""

    return current_user
