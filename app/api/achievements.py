from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from ..db.session import SessionDep
from ..db.models import Achievement, UserAchievement, User, Role
from ..utils.dependencies import get_current_user
from ..db.models import User

router = APIRouter()

@router.post("/", response_model=Achievement)
def create_achievement(
    achievement: Achievement,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.role == Role.admin:
        achievement.is_global = True
        achievement.user_id = None
    else:
        achievement.is_global = False
        achievement.user_id = current_user.id

    session.add(achievement)
    session.commit()
    session.refresh(achievement)
    return achievement



@router.get("/", response_model=list[Achievement])
def read_achievements(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    all: bool = False,   
):
    if current_user.role == Role.admin:
        if all:
            query = select(Achievement) 
        else:
            query = select(Achievement).where(Achievement.is_global == True)
    else:
        query = select(Achievement).where(
            (Achievement.is_global == True) | (Achievement.user_id == current_user.id)
        )

    return session.exec(query.offset(offset).limit(limit)).all()



@router.get("/{achievement_id}", response_model=Achievement)
def read_achievement(
    achievement_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    achievement = session.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    if current_user.role != Role.admin:
        if not (achievement.is_global or achievement.user_id == current_user.id):
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return achievement



@router.delete("/{achievement_id}")
def delete_achievement(
    achievement_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    achievement = session.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    if current_user.role == Role.admin:
        if not achievement.is_global:
            raise HTTPException(status_code=403, detail="Admins can only delete global achievements")
    else:
        if achievement.is_global or achievement.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(achievement)
    session.commit()
    return {"ok": True}


@router.post("/user/", response_model=UserAchievement)
def create_user_achievement(user_achievement: UserAchievement, session: SessionDep):
    session.add(user_achievement)
    session.commit()
    session.refresh(user_achievement)
    return user_achievement

@router.get("/user/", response_model=list[UserAchievement])
def read_user_achievements(
    session: SessionDep,
    user_id: int | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    query = select(UserAchievement)
    if user_id:
        query = query.where(UserAchievement.user_id == user_id)
    return session.exec(query.offset(offset).limit(limit)).all()

@router.get("/user/{ua_id}", response_model=UserAchievement)
def read_user_achievement(ua_id: int, session: SessionDep):
    ua = session.get(UserAchievement, ua_id)
    if not ua:
        raise HTTPException(status_code=404, detail="UserAchievement not found")
    return ua

@router.delete("/user/{ua_id}")
def delete_user_achievement(ua_id: int, session: SessionDep):
    ua = session.get(UserAchievement, ua_id)
    if not ua:
        raise HTTPException(status_code=404, detail="UserAchievement not found")
    session.delete(ua)
    session.commit()
    return {"ok": True}
