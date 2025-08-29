from sqlalchemy.orm import Session
from ..db.models import User, Role
from app.core.security import verify_password
from fastapi import HTTPException

def require_role(user: User, roles: list[Role]):
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Not enough permissions")


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
