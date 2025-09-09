from typing import Annotated
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select
from ..db.models import Habit, User, Streak, Achievement, UserAchievement
from ..db.response_model import HabitWithStreak
from ..db.session import SessionDep
from ..utils.dependencies import get_current_user
from datetime import date, timedelta
from math import floor, sqrt
import json
from ..utils.check_condition import check_condition

def check_and_grant_achievements(session, user: User, habit: Habit, streak: Streak):
    achievements = session.exec(
        select(Achievement).where(
            (Achievement.is_global == True) | (Achievement.user_id == user.id)
        )
    ).all()
    user_achievements = session.exec(
        select(UserAchievement).where(UserAchievement.user_id == user.id)
    ).all()
    obtained_ids = {ua.achievement_id for ua in user_achievements}
    for ach in achievements:
        if ach.id in obtained_ids:
            continue
        cond = ach.condition if isinstance(ach.condition, dict) else json.loads(ach.condition)
        if check_condition(cond, streak, user):
            ua = UserAchievement(
                user_id=user.id,
                achievement_id=ach.id,
                habit_id=habit.id,
                obtained=True
            )
            session.add(ua)

    session.commit()

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

    streak = Streak(
        user_id=current_user.id,
        habit_id=habit.id,
        current_streak=0,
        longest_streak=0,
        last_completed=None
    )
    session.add(streak)
    session.commit()
    return habit


@router.post("/{habit_id}/complete", response_model=Habit)
def complete_habit(
    habit_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Habit:
    db_habit = session.get(Habit, habit_id)
    if not db_habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if db_habit.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    streak = session.exec(
        select(Streak).where(
            Streak.habit_id == habit_id,
            Streak.user_id == current_user.id
        )
    ).first()

    if not streak:
        raise HTTPException(status_code=404, detail="Streak not found")

    today = date.today()
    freq = db_habit.frequency  

    if streak.last_completed == today:
        raise HTTPException(status_code=400, detail="Habit already completed today")

    if streak.last_completed == today - timedelta(days=freq):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_completed = today

    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    session.add(streak)

    user = session.get(User, current_user.id)
    user.xp += 5 * freq if freq > 1 else 10
    user.level = floor(sqrt(user.xp) / 10)
    session.add(user)

    session.commit()
    session.refresh(user)
    session.refresh(db_habit)
    session.refresh(streak)

    check_and_grant_achievements(session, user, db_habit, streak)

    return db_habit


@router.get("/", response_model=list[HabitWithStreak])
def read_my_habits(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):

    habits = session.exec(
        select(Habit)
        .where(Habit.owner_id == current_user.id)
        .offset(offset)
        .limit(limit)
    ).all()

    streaks = session.exec(
        select(Streak).where(Streak.user_id == current_user.id)
    ).all()

    streak_map = {s.habit_id: s for s in streaks}

    results = []
    for habit in habits:
        results.append(HabitWithStreak(
            id=habit.id,
            name=habit.title,
            description=habit.description,
            frequency = habit.frequency,
            streak=streak_map.get(habit.id)  
        ))

    return results


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
    current_user: Annotated[User, Depends(get_current_user)]
):
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if habit.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    streak = session.exec(
        select(Streak).where(Streak.habit_id == habit.id, Streak.user_id == habit.owner_id)
    ).first()
    if streak:
        session.delete(streak)

    user_achievements = session.exec(
        select(UserAchievement).where(UserAchievement.habit_id == habit.id)
    ).all()
    for ua in user_achievements:
        session.delete(ua)

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
