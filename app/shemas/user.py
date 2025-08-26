from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str | None = "User"

class UserRead(BaseModel):
    id: int
    username: str
    nickname: str | None
