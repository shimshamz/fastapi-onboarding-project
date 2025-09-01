from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.core.db import create_db_and_tables
from app.api.main import api_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(api_router)