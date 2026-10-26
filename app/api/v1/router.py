from fastapi import APIRouter
from app.api.v1.users import router as users_router

app_router = APIRouter()
app_router.include_router(users_router)
