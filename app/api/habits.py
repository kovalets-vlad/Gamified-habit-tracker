from typing import Annotated
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select
from ..db.models import Habit, User 
from ..db.session import SessionDep
from ..utils.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=Habit)
def create_habit(
    habit: Habit,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Habit:
    habit.owner_id = current_user.id
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@router.get("/", response_model=list[Habit])
def read_my_habits(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Habit]:
    habits = session.exec(
        select(Habit).where(Habit.owner_id == current_user.id).offset(offset).limit(limit)
    ).all()
    return habits


@router.get("/{habit_id}", response_model=Habit)
def read_habit(
    habit_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Habit:
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if habit.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return habit


@router.put("/{habit_id}", response_model=Habit)
def update_habit(
    habit_id: int,
    updated_habit: Habit,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Habit:
    db_habit = session.get(Habit, habit_id)
    if not db_habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if db_habit.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = updated_habit.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_habit, key, value)

    session.add(db_habit)
    session.commit()
    session.refresh(db_habit)
    return db_habit


@router.delete("/{habit_id}")
def delete_habit(
    habit_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if habit.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(habit)
    session.commit()
    return {"ok": True}


@router.get("/user/{user_id}", response_model=list[Habit])
def read_habits_by_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Habit]:
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    habits = session.exec(
        select(Habit).where(Habit.owner_id == user_id).offset(offset).limit(limit)
    ).all()
    if not habits:
        raise HTTPException(status_code=404, detail="No habits found for this user")
    return habits
