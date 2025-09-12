from pydantic import BaseModel

class BuyItemRequest(BaseModel):
    item_id: int
    currency: str  

class EquipItemRequest(BaseModel):
    user_item_id: int