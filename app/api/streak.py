from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select
from ..db.session import SessionDep
from ..db.models import Streak
from ..db.models import User
from ..utils.dependencies import get_current_user


router = APIRouter()

@router.get("", response_model=list[Streak])
def read_streaks(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: int | None = None,
    habit_id: int | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    query = select(Streak)
    if user_id:
        query = query.where(Streak.user_id == user_id)
    if habit_id:
        query = query.where(Streak.habit_id == habit_id)
    return session.exec(query.offset(offset).limit(limit)).all()

@router.get("/{streak_id}", response_model=Streak)
def read_streak(streak_id: int, session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    streak = session.get(Streak, streak_id)
    if not streak:
        raise HTTPException(status_code=404, detail="Streak not found")
    return streak
