from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from datetime import datetime
from ..db.session import SessionDep
from ..db.models import Achievement, UserAchievement, Streak
from ..utils.dependencies import get_current_user
from ..db.models import User

router = APIRouter()

@router.post("/streak/", response_model=Streak)
def create_streak(streak: Streak, session: SessionDep):
    session.add(streak)
    session.commit()
    session.refresh(streak)
    return streak

@router.get("/streak/", response_model=list[Streak])
def read_streaks(
    session: SessionDep,
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

@router.get("/streak/{streak_id}", response_model=Streak)
def read_streak(streak_id: int, session: SessionDep):
    streak = session.get(Streak, streak_id)
    if not streak:
        raise HTTPException(status_code=404, detail="Streak not found")
    return streak

@router.put("/streak/{streak_id}", response_model=Streak)
def update_streak(streak_id: int, updated_streak: Streak, session: SessionDep):
    db_streak = session.get(Streak, streak_id)
    if not db_streak:
        raise HTTPException(status_code=404, detail="Streak not found")

    update_data = updated_streak.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_streak, key, value)

    session.add(db_streak)
    session.commit()
    session.refresh(db_streak)
    return db_streak

@router.delete("/streak/{streak_id}")
def delete_streak(streak_id: int, session: SessionDep):
    streak = session.get(Streak, streak_id)
    if not streak:
        raise HTTPException(status_code=404, detail="Streak not found")
    session.delete(streak)
    session.commit()
    return {"ok": True}
