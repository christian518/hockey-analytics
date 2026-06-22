from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/checkout")
async def create_checkout(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"message": "Payments not configured", "already_owned": True}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    return {"status": "ok"}

@router.get("/access/{game_id}")
async def check_access(game_id: str, current_user: User = Depends(get_current_user)):
    return {"has_access": True, "access_level": "full"}