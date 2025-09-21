from typing import Annotated
from fastapi import HTTPException, Depends   
from sqlmodel import select
from fastapi import APIRouter
from ..db.models import User, UserWallet, UserItem, ShopItem
from ..shemas.market import EquipItemRequest
from ..db.session import SessionDep
from ..core.security import get_password_hash
from ..utils.dependencies import get_current_user
from ..utils.users import require_role


router = APIRouter()

@router.post("/", response_model=User)
def create_user(
    user: User,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)], 
) -> User:
    require_role(current_user, roles="admin") 

    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)

    wallet = UserWallet(user_id=user.id, coins=0, gems=0, event_tokens=0)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)

    return user


@router.get("/", response_model=list[User])
def read_users(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)], 
    offset: int = 0,
    limit: int = 100,
):
    require_role(current_user, roles="admin") 
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)], 
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_role(current_user, roles="admin")  

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.get("/me/", response_model=User)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

@router.put("/update-password/", response_model=User)
def update_password(
    new_password: str,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = get_password_hash(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# -----------------------------
# Users leaderboard
# -----------------------------

@router.get("/leaderboard/", response_model=list[User])
def read_leaderboard(
    current_user: Annotated[User, Depends(get_current_user)], 
    session: SessionDep,
    limit: int = 10,
):
    users = session.exec(
        select(User).order_by(User.xp.desc()).limit(limit)
    ).all()

    return users

# -----------------------------
# User wallet
# -----------------------------

@router.get("/wallet/")
def get_user_wallet(
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
):
    wallet = session.exec(select(UserWallet).where(UserWallet.user_id == current_user.id)).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

# -----------------------------
# List user items
# -----------------------------

@router.get("/items/")
def list_user_items(
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
):
    items = session.exec(select(UserItem).where(UserItem.user_id == current_user.id)).all()
    return items

# -----------------------------
# Equip item
# -----------------------------

@router.post("/equip/")
def equip_item(
    request: EquipItemRequest, 
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 

):
    user_item = session.get(UserItem, request.user_item_id)
    if not user_item or user_item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found for user")

    item = session.get(ShopItem, user_item.item_id)
    same_type_items = session.exec(
        select(UserItem).join(ShopItem).where(
            (UserItem.user_id == current_user.id) & 
            (UserItem.is_equipped == True) & 
            (ShopItem.type == item.type)
        )
    ).all()

    for i in same_type_items:
        i.is_equipped = False
        session.add(i)

    user_item.is_equipped = True
    session.add(user_item)
    session.commit()
    return {"success": True, "message": "Item equipped"}

# -----------------------------
# Unequip item
# -----------------------------

@router.post("/unequip/")
def unequip_item(
    request: EquipItemRequest, 
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
):
    user_item = session.get(UserItem, request.user_item_id)
    if not user_item or user_item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found for user")

    user_item.is_equipped = False
    session.add(user_item)
    session.commit()
    return {"success": True, "message": "Item unequipped"}