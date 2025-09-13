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

class Currency(str, Enum):
    COINS = "coins"
    GEMS = "gems"
    EVENT_TOKENS = "event_tokens"

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
    gems_reward: int = 0 
    created_at: datetime = Field(default_factory=datetime.utcnow)

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

class MedalAchievementLink(SQLModel, table=True):
    __tablename__ = "medal_achievement_link"

    medal_id: int = Field(foreign_key="medals.id", primary_key=True)
    achievement_id: int = Field(foreign_key="achievements.id", primary_key=True)

class ShopItem(SQLModel, table=True):
    __tablename__ = "shop_items"

    id: int = Field(primary_key=True)
    name: str
    description: str | None = None
    need_xp: int = 0    
    price: int = 0    
    currency: Currency = Field(default=Currency.COINS) 
    type: str                 
    rarity: str | None = None 
    icon_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserItem(SQLModel, table=True):
    __tablename__ = "user_items"

    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    item_id: int = Field(foreign_key="shop_items.id")
    is_equipped: bool = False 
    acquired_at: datetime = Field(default_factory=datetime.utcnow)

class UserWallet(SQLModel, table=True):
    __tablename__ = "user_wallets"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    coins: int = Field(default=0)
    gems: int = Field(default=0)  
    event_tokens: int = Field(default=0)  

class Quest(SQLModel, table=True):
    __tablename__ = "quests"

    id: int = Field(primary_key=True)
    title: str
    description: str
    type: str  # daily / weekly / special
    condition: dict = Field(sa_column=Column(JSONEncodedDict))  
    xp_reward: int = 0
    coin_reward: int = 0
    event_tokens_reward: int = 0
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_active: bool = Field(default=True)

class UserQuest(SQLModel, table=True):
    __tablename__ = "user_quests"

    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    quest_id: int = Field(foreign_key="quests.id")
    completed: bool = Field(default=False)
    completed_at: datetime | None = None







