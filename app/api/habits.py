from typing import Annotated
from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select
from ..db.models import Habit
from ..db.session import SessionDep

router = APIRouter()

@router.post("/habits/")
def create_habit(habit: Habit, session: SessionDep) -> Habit:
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@router.get("/habits/")
def read_habits(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Habit]:
    habits = session.exec(select(Habit).offset(offset).limit(limit)).all()
    return habits


@router.get("/habits/{habit_id}")
def read_habit(habit_id: int, session: SessionDep) -> Habit:
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.put("/habits/{habit_id}")
def update_habit(habit_id: int, updated_habit: Habit, session: SessionDep) -> Habit:
    db_habit = session.get(Habit, habit_id)
    if not db_habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    update_data = updated_habit.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_habit, key, value)

    session.add(db_habit)
    session.commit()
    session.refresh(db_habit)
    return db_habit


@router.delete("/habits/{habit_id}")
def delete_habit(habit_id: int, session: SessionDep):
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    session.delete(habit)
    session.commit()
    return {"ok": True}

@router.get("/habits/user/{user_id}")
def read_habits_by_user(
    user_id: int,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Habit]:
    habits = session.exec(
        select(Habit).where(Habit.owner_id == user_id).offset(offset).limit(limit)
    ).all()
    if not habits:
        raise HTTPException(status_code=404, detail="No habits found for this user")
    return habits

