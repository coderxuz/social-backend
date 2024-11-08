from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Request,
    Depends,
)
from builtins import int
from app.database import get_db
from sqlalchemy.orm import Session
from app.api.auth import oauth2_scheme
from app.schemas import Followings, Message, Followers
from app.utils import get_user_from_token, follow_user, check_user_by_username,unfollow
from app.models import User

router = APIRouter(prefix="/followings", tags=["FOLLOWINGS"])

@router.post('/follow', response_model=Message, dependencies=[Depends(get_db)])
async def follow(data:Followings,request:Request, db: Session= Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    following_user = check_user_by_username(data.username, db=db)
    following = await follow_user(current_user=db_user, user_for_following=following_user, db=db)
    return following
@router.get('/followers', dependencies=[Depends(oauth2_scheme)])
async def followers(request:Request, db:Session= Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    followers:list[User] = db_user.followers
    followers_list = []
    for user in followers:
        if user.user_img:
            followers_list.append(
                {
                    'id':user.id,
                    'username':user.username,
                    'user_image':f"{request.url.scheme}://{request.url.netloc}/image/{user.user_img}",
                }
            )
        else:
            followers_list.append(
                {
                    'id':user.id,
                    'username':user.username,
                    'user_image':user.user_img
                }
            )
    return followers_list
@router.post('/unfollow')
async def unfollowing(data:Followings,request:Request, db: Session= Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    user_unfollow = check_user_by_username(user_username=data.username, db=db)
    unfollow_response = await unfollow(current_user=db_user, user_for_unfollowing=user_unfollow, db=db)
    return unfollow_response
