from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column
from .response_model import JSONEncodedDict

class Role(str, Enum):
    admin = "admin"
    user = "user"
    manager = "manager"
    moderator = "moderator"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    nickname: Optional[str] = Field(default="User")
    password: str
    role: Role = Field(default=Role.user)
    xp: int = Field(default=0)
    level: int = Field(default=1)


    habits: List["Habit"] = Relationship(back_populates="owner")

class Habit(SQLModel, table=True):
    __tablename__ = "habits"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    frequency: int = Field(default=1) 
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")

    owner: Optional[User] = Relationship(back_populates="habits")

class Achievement(SQLModel, table=True):
    __tablename__ = "achievements"

    id: int = Field(primary_key=True)
    title: str
    description: str | None = None
    condition: dict = Field(sa_column=Column(JSONEncodedDict)) 
    is_global: bool = True  
    user_id: int | None = Field(default=None, foreign_key="users.id")  
    created_at: datetime = Field(default_factory=datetime.utcnow)

    medal: Optional["Medal"] = Relationship(back_populates="achievements")

class UserAchievement(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    achievement_id: int = Field(foreign_key="achievements.id")
    habit_id: int | None = Field(default=None, foreign_key="habits.id")
    obtained: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Streak(SQLModel, table=True):
    __tablename__ = "streaks"

    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    habit_id: int = Field(foreign_key="habits.id")
    current_streak: int = 0
    longest_streak: int = 0
    last_completed: date | None = None  

class Medal(SQLModel, table=True):
    __tablename__ = "medals"

    id: int = Field(primary_key=True)
    name: str
    xp_reward: int = 0
    icon_url: str | None = None  

    achievements: list["Achievement"] = Relationship(back_populates="medal")

class MedalAchievementLink(SQLModel, table=True):
    __tablename__ = "medal_achievement_link"

    medal_id: int = Field(foreign_key="medals.id", primary_key=True)
    achievement_id: int = Field(foreign_key="achievements.id", primary_key=True)



