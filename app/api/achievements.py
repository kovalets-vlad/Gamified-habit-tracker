from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from ..db.session import AsyncSessionDep
from ..db.models import Achievement, UserAchievement, User, Habit, Streak, UserWallet
from ..utils.dependencies import get_current_user
from ..utils.users import require_role
from ..db.response_model import UserAchievementRead
import json
from ..utils.check_condition import check_condition

router = APIRouter()


# -------------------------------
# ACHIEVEMENTS CRUD
# -------------------------------

@router.post("/", response_model=Achievement)
async def create_achievement(
    achievement: Achievement,
    session: AsyncSessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    require_role(current_user, roles="admin")
    session.add(achievement)
    await session.commit()
    await session.refresh(achievement)
    return achievement


@router.get("/", response_model=list[Achievement])
async def read_achievements(
    session: AsyncSessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    query = select(Achievement)
    result = await session.exec(query.offset(offset).limit(limit))
    return result.all()


@router.get("/{achievement_id}", response_model=Achievement)
async def read_achievement(
    achievement_id: int,
    session: AsyncSessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    require_role(current_user, roles=["admin"])
    achievement = await session.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return achievement


@router.delete("/{achievement_id}")
async def delete_achievement(
    achievement_id: int,
    session: AsyncSessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    require_role(current_user, roles=["admin"])
    achievement = await session.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    await session.delete(achievement)
    await session.commit()
    return {"ok": True}


# -------------------------------
# USER ACHIEVEMENTS
# -------------------------------

@router.post("/user/", response_model=UserAchievement)
async def create_user_achievement(user_achievement: UserAchievement, session: AsyncSessionDep):
    session.add(user_achievement)
    await session.commit()
    await session.refresh(user_achievement)
    return user_achievement


@router.get("/user/", response_model=list[UserAchievementRead])
async def read_user_achievements(
    session: AsyncSessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    query = select(UserAchievement).where(UserAchievement.user_id == current_user.id)
    result = await session.exec(query.offset(offset).limit(limit))
    return result.all()


@router.get("/user/{ua_id}", response_model=UserAchievement)
async def read_user_achievement(ua_id: int, session: AsyncSessionDep):
    ua = await session.get(UserAchievement, ua_id)
    if not ua:
        raise HTTPException(status_code=404, detail="UserAchievement not found")
    return ua


@router.delete("/user/{ua_id}")
async def delete_user_achievement(ua_id: int, session: AsyncSessionDep):
    ua = await session.get(UserAchievement, ua_id)
    if not ua:
        raise HTTPException(status_code=404, detail="UserAchievement not found")
    await session.delete(ua)
    await session.commit()
    return {"ok": True}


# -------------------------------
# CHECK AND GRANT ACHIEVEMENTS
# -------------------------------

async def check_and_grant_achievements(session: AsyncSessionDep, user: User, habit: Habit, streak: Streak):
    achievements_result = await session.exec(select(Achievement))
    achievements = achievements_result.all()

    obtained_result = await session.exec(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    )
    obtained_ids = set(obtained_result.all())

    wallet_result = await session.exec(select(UserWallet).where(UserWallet.user_id == user.id))
    wallet = wallet_result.first()

    for ach in achievements:
        if ach.id in obtained_ids:
            continue

        cond = ach.condition if isinstance(ach.condition, dict) else json.loads(ach.condition)
        if check_condition(cond, streak, user):
            ua1 = UserAchievement(
                user_id=user.id,
                achievement_id=ach.id,
                habit_id=habit.id,
                obtained=True
            )
            session.add(ua1)

            ua2 = UserAchievement(
                user_id=user.id,
                achievement_id=ach.id,
                habit_id=None,
                obtained=True
            )
            session.add(ua2)

            if wallet:
                gems_reward = getattr(ach, "gems_reward", 1)
                wallet.gems += gems_reward
                session.add(wallet)

    await session.commit()
