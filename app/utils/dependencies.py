from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from ..db.models import User
from ..db.session import SessionDep
from ..core.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")  

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = session.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
