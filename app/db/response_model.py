from pydantic import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy.types import TypeDecorator, TEXT
import json

class UserAchievementRead(BaseModel):
    id: int
    user_id: int
    achievement_id: int
    habit_id: int | None
    obtained: bool

    class Config:
        from_attributes = True  


class JSONEncodedDict(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)



class StreakOut(BaseModel):
    current_streak: int
    longest_streak: int
    last_completed: Optional[date] = None

    class Config:
        from_attributes = True   

class HabitWithStreak(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    frequency: Optional[int] = None
    streak: Optional[StreakOut] = None

    class Config:
        from_attributes = True   
