from typing import Annotated
from fastapi import Query, HTTPException
from sqlmodel import select
from fastapi import APIRouter
from ..db.models import User
from ..db.session import SessionDep

router = APIRouter()

@router.post("/users/")
def create_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/users/")
def read_useres(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    Useres = session.exec(select(User).offset(offset).limit(limit)).all()
    return Useres

@router.get("/users/{user_id}")
def read_hero(users_id: int, session: SessionDep) -> User:
    user = session.get(User, users_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}")
def delete_hero(hero_id: int, session: SessionDep):
    user = session.get(User, hero_id)
    if not user:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(user)
    session.commit()
    return {"ok": True}