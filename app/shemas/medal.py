from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class MedalBase(BaseModel):
    name: str
    xp_reward: Optional[int] = None
    icon_url: Optional[str] = None

class MedalCreate(MedalBase):
    pass

class MedalUpdate(MedalBase):
    pass

class MedalOut(MedalBase):
    id: UUID

    class Config:
        orm_mode = True