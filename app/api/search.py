from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session
from app.api.auth import oauth2_scheme
from app.database import get_db
from app.models import User
from app.utils import has_followed, get_user_from_token

router = APIRouter(prefix="/search", tags=["SEARCH"])

@router.get("")
async def search(
    request: Request,
    username: str = Query(..., description="Username to search for"),
    db: Session = Depends(get_db),
):
    current_user = await get_user_from_token(request=request, database=db)
    db_user = db.query(User).filter(User.username.ilike(f"{username}%")).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    return {
        "username": db_user.username,
        "user_img": (
            f"{request.url.scheme}://{request.url.netloc}/image/{db_user.user_img}"
            if db_user.user_img
            else None
        ),
        "has_followed": await has_followed(
            current_user=current_user, user_followed_id=db_user.id, db=db
        ),
    }
