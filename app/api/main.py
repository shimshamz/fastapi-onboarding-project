from fastapi import APIRouter

from app.api.routes import users, login, academic_institutions

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(academic_institutions.router)
