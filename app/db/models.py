from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    nickname: Optional[str] = Field(default="User")
    password: str

    habits: List["Habit"] = Relationship(back_populates="owner")


class Habit(SQLModel, table=True):
    __tablename__ = "habits"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")

    owner: Optional[User] = Relationship(back_populates="habits")
