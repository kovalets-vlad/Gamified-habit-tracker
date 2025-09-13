from fastapi import HTTPException, APIRouter, Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from ..db.models import User, ShopItem, UserItem, UserWallet
from ..db.session import SessionDep
from ..shemas.market import BuyItemRequest
from typing import Annotated
from ..utils.dependencies import get_current_user

router = APIRouter()

@router.get("/shop/items/")
def list_shop_items(
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
):
    items = session.exec(select(ShopItem)).all()
    return items

@router.get("/shop/items/{item_id}")
def get_shop_item(
    item_id: int, 
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
):
    item = session.get(ShopItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# -----------------------------
# Purchase item
# -----------------------------

@router.post("/shop/buy/")
def buy_item(
    request: BuyItemRequest, 
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
):

    item = session.get(ShopItem, request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    wallet = session.exec(select(UserWallet).where(UserWallet.user_id == current_user.id)).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if request.currency not in ["coins", "gems", "event_tokens"]:
        raise HTTPException(status_code=400, detail="Invalid currency")

    cost = getattr(item, "price") if request.currency == "coins" else getattr(item, request.currency, 0)
    current_balance = getattr(wallet, request.currency)

    if current_balance < cost:
        raise HTTPException(status_code=400, detail=f"Not enough {request.currency}")

    if item.need_xp > 0:
        user = session.get(User, current_user.id)
        if user.xp < item.need_xp:
            raise HTTPException(status_code=400, detail="Not enough XP")

    try:
        setattr(wallet, request.currency, current_balance - cost)
        session.add(wallet)
        user_item = UserItem(user_id=current_user.id, item_id=item.id, is_equipped=False)
        session.add(user_item)
        session.commit()
        session.refresh(user_item)
        return {"success": True, "message": "Item purchased successfully", "user_item_id": user_item.id}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to purchase item")

# -----------------------------
# List user items
# -----------------------------
@router.get("/users/{user_id}/items/")
def list_user_items(
    user_id: int, 
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
):
    items = session.exec(select(UserItem).where(UserItem.user_id == user_id)).all()
    return items
