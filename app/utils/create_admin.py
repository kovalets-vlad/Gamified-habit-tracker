from sqlmodel import Session, select
from ..db.base import engine
from ..db.models import User, Role
from ..core.security import get_password_hash


def create_admin():
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.role == "admin")).first()
        if not admin:
            admin = User(
                username="TEST",
                nickname="Admin",
                password=get_password_hash("111"), 
                role=Role.admin
            )
            session.add(admin)
            session.commit()
            print("✅ Admin user created: TEST / 111")
        else:
            print("ℹ️ Admin user already exists")
