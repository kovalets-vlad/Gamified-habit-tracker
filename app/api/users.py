from typing import Annotated
from fastapi import HTTPException, Depends   
from sqlmodel import select
from fastapi import APIRouter
from ..db.models import User
from ..db.session import SessionDep
from ..core.security import get_password_hash
from ..utils.dependencies import get_current_user
from ..utils.users import require_role

router = APIRouter()

# @router.post("/") 
# def create_user(user: User, session: SessionDep) -> User: 
#     user.password = get_password_hash(user.password) 
#     session.add(user) 
#     session.commit() 
#     session.refresh(user) 
#     return user

@router.post("/", response_model=User)
def create_user(
    user: User,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)], 
) -> User:
    require_role(current_user, roles="admin") 
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=list[User])
def read_users(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)], 
    offset: int = 0,
    limit: int = 100,
):
    require_role(current_user, roles="admin") 
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)], 
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_role(current_user, roles="admin")  

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
