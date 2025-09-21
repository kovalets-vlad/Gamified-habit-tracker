from datetime import datetime  
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from ..db.models import Quest, User, UserQuest, UserWallet, Streak
from ..db.session import SessionDep
from typing import Annotated
from ..utils.dependencies import get_current_user
from ..utils.users import require_role
from ..utils.check_condition import check_condition
router = APIRouter()

@router.post("/", response_model=Quest)
def create_quest(
    quest: Quest,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    require_role(current_user, roles=["admin", "manager"])

    session.add(quest)
    session.commit()
    session.refresh(quest)
    return quest


@router.get("/", response_model=list[Quest])
def read_quests(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    now = datetime.utcnow()
    quests = session.exec(
        select(Quest).where(
            Quest.is_active == True,
            (Quest.start_date == None) | (Quest.start_date <= now),
            (Quest.end_date == None) | (Quest.end_date >= now),
        )
    ).all()
    return quests


@router.post("/{quest_id}/complete")
def complete_quest(
    quest_id: int,
    session: SessionDep,
    streak: Streak,
    current_user: Annotated[User, Depends(get_current_user)]
):
    quest = session.get(Quest, quest_id)
    if not quest or not quest.is_active:
        raise HTTPException(status_code=404, detail="Quest not found or inactive")

    now = datetime.utcnow()
    if quest.start_date and now < quest.start_date:
        raise HTTPException(status_code=400, detail="Quest not started yet")
    if quest.end_date and now > quest.end_date:
        raise HTTPException(status_code=400, detail="Quest expired")
    if quest.is_active is False:
        raise HTTPException(status_code=400, detail="Quest is inactive")
    
    if not check_condition(quest.condition, streak, current_user):
        raise HTTPException(status_code=400, detail="Quest conditions not met")

    user_quest = session.exec(
        select(UserQuest).where(
            UserQuest.user_id == current_user.id,
            UserQuest.quest_id == quest_id
        )
    ).first()

    if user_quest and user_quest.completed:
        raise HTTPException(status_code=400, detail="Quest already completed")

    if not user_quest:
        user_quest = UserQuest(user_id=current_user.id, quest_id=quest_id)

    user_quest.completed = True
    user_quest.completed_at = now

    current_user.xp += quest.xp_reward
    wallet = session.exec(
        select(UserWallet).where(UserWallet.user_id == current_user.id)
    ).first()
    if wallet:
        wallet.coins += quest.coin_reward
        wallet.event_tokens += quest.event_tokens_reward

    session.add_all([user_quest, current_user, wallet])
    session.commit()
    return {"message": "Quest completed", "rewards": quest}


@router.delete("/{quest_id}")
def delete_quest(
    quest_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    require_role(current_user, roles=["admin", "manager"])

    quest = session.get(Quest, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")

    quest.is_active = False
    session.add(quest)
    session.commit()
    return {"message": "Quest deactivated"}
