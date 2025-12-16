from fastapi import APIRouter, Depends, status

from app.api.dependencies import DBDep, get_current_user

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/")
async def get_all_roles(db: DBDep):
    return {"message": "Roles endpoint"}
