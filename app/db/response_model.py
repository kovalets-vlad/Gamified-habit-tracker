from pydantic import BaseModel
from typing import Optional
from datetime import date

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
    streak: Optional[StreakOut] = None

    class Config:
        from_attributes = True   
