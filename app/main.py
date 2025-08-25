from fastapi import FastAPI
from app.api import users, habits
from .db.init_db import create_db_and_tables

app = FastAPI(title="Gamified Habit Tracker")
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
app.include_router(users.router, tags=["Users"])

