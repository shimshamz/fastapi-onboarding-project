from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.core.db import engine, create_db_and_tables
from app.api.main import api_router

from app import crud, models
from sqlmodel import Session, select

def startup_populate_users():
    with Session(engine) as session:
        # Check if users already exist
        statement = select(models.User)
        results = session.exec(statement).first()
        if results:
            return # Skip if users exist

        dummy_users = [
            models.UserCreate(email="bob@test.com", is_active=True, is_superuser=True, full_name="Bob Jones", password="secretpw"),
            models.UserCreate(email="tom@test.com", is_active=True, is_superuser=False, full_name="Tom Locke", password="secretpw2")
        ]
        for user in dummy_users:
            crud.create_user(session=session, user_create=user)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    startup_populate_users()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(api_router)