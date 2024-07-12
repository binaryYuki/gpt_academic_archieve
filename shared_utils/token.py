import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dateutil.tz import tzutc
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

# to get a string like this run:
# openssl rand - hex 32
# SECRET_KEY = os.environ.get("JWT_KEY")
SECRET_KEY = "b1d4b1f3d4b1d4b1f3d4b1d4b1f3d4b1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


# generate token:
#   -- param: email
#   -- expires: 30 minutes
def create_access_token(email: str):
    expire = datetime.now(tzutc()) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")


# decode token:
#   -- param: token
#   -- returns: email
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
