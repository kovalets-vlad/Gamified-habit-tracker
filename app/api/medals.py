from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..db.models import Medal, User, Role, MedalAchievementLink
from ..shemas.medal import MedalCreate, MedalOut, MedalUpdate
from ..utils.dependencies import get_current_user
from ..utils.users import require_role
from ..db.session import SessionDep

router = APIRouter()


@router.post("/", response_model=MedalOut, status_code=status.HTTP_201_CREATED)
def create_medal(
    medal_in: MedalCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, [Role.admin])
    medal = Medal(**medal_in.dict())
    session.add(medal)
    session.commit()
    session.refresh(medal)
    return medal


@router.get("/", response_model=List[MedalOut])
def list_medals(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    medals = session.query(Medal).all()
    return medals


@router.get("/{medal_id}", response_model=MedalOut)
def get_medal(
    medal_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    medal = session.query(Medal).filter(Medal.id == medal_id).first()
    if not medal:
        raise HTTPException(status_code=404, detail="Medal not found")
    return medal


@router.put("/{medal_id}", response_model=MedalOut)
def update_medal(
    medal_id: int,
    medal_in: MedalUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, [Role.admin])
    medal = session.query(Medal).filter(Medal.id == medal_id).first()
    if not medal:
        raise HTTPException(status_code=404, detail="Medal not found")
    for field, value in medal_in.dict(exclude_unset=True).items():
        setattr(medal, field, value)
    session.commit()
    session.refresh(medal)
    return medal


@router.delete("/{medal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medal(
    medal_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, [Role.admin])
    medal = session.query(Medal).filter(Medal.id == medal_id).first()
    if not medal:
        raise HTTPException(status_code=404, detail="Medal not found")
    session.query(MedalAchievementLink).filter(MedalAchievementLink.medal_id == medal_id).delete()
    session.delete(medal)
    session.commit()
    return {"ok": True}

@router.post("/{medal_id}/achievements/{achievement_id}", status_code=status.HTTP_201_CREATED)
def link_achievement_to_medal(  
    medal_id: int,
    achievement_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, [Role.admin])
    medal = session.query(Medal).filter(Medal.id == medal_id).first()
    if not medal:
        raise HTTPException(status_code=404, detail="Medal not found")
    achievement_link = MedalAchievementLink(medal_id=medal_id, achievement_id=achievement_id)
    session.add(achievement_link)
    session.commit()
    return {"ok": True}

@router.delete("/{medal_id}/achievements/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_achievement_from_medal(  
    medal_id: int,
    achievement_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, [Role.admin])
    medal = session.query(Medal).filter(Medal.id == medal_id).first()
    if not medal:
        raise HTTPException(status_code=404, detail="Medal not found")
    achievement_link = session.query(MedalAchievementLink).filter(
        MedalAchievementLink.medal_id == medal_id,
        MedalAchievementLink.achievement_id == achievement_id
    ).first()
    if not achievement_link:
        raise HTTPException(status_code=404, detail="Link not found")
    session.delete(achievement_link)
    session.commit()
    return {"ok": True}

