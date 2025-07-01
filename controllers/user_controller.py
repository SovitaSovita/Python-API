from fastapi import APIRouter, Depends
from auth import get_current_user
from models import User

router = APIRouter(
    prefix="/api/v1",        # ← This is like renaming the "controller"
    tags=["User Controller"]  # ← This name will show in Swagger UI
)

@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email
    }
