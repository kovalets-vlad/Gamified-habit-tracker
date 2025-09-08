from fastapi import FastAPI
from app.api import users, habits, auth, achievements, streak
from .db.init_db import create_db_and_tables

app = FastAPI(title="Gamified Habit Tracker")
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(users.router, prefix="/streak", tags=["Users"])
app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])


