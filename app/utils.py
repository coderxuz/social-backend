from builtins import int
from fastapi import HTTPException, status, Request, Depends, UploadFile
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User, Post, Like, Comment
from typing import Optional, Dict, Any
from jose import jwt, JWTError
import os

def check_user_by_email(
    user_email: str, db: Session = Depends(get_db)
) -> Optional[User]:
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user1 not found"
        )
    return db_user


def check_user_by_username(
    user_username: str, db: Session = Depends(get_db)
) -> Optional[User]:
    db_user = db.query(User).filter(User.username == user_username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user2 not found"
        )
    return db_user
async def check_user_by_id(
    user_id: int, db: Session = Depends(get_db)
) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user1 not found"
        )
    return db_user


def get_token_from_header(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token doesn't exist"
            
        )
    scheme , _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Bearer format is wrong') 
    return token   
def verify_token(request: Request)->Optional[Dict[str, Any]]:
    from app.api.auth import SECRET_KEY, ALGORITHM
    token = get_token_from_header(request)
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong or expired token')

async def save_image(file:UploadFile)->Optional[str]:
    save_folder = 'images'
    image_types = ['image/jpg','image/png','image/gif', 'image/jpeg']
    if file.content_type not in image_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'image type is incorrect {UploadFile.content_type}')
    
    os.makedirs(save_folder, exist_ok=True)
    file_path = os.path.join(save_folder, file.filename)
    
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    return file_path

async def get_user_from_token(request: Request, database:Session = Depends(get_db)):
    payload = verify_token(request)
    username = payload['sub']
    db_user = check_user_by_username(user_username=username, db=database)
    return db_user

async def like_post(user_id:int,post_id:int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id  == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    like = Like(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()
    return {'message':'liked'}
async def has_liked(user_id:int, post_id:int, db: Session = Depends(get_db))-> bool:
    post = db.query(Post).filter(Post.id  == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    like = db.query(Like).filter_by(user_id=user_id, post_id=post_id).first()
    if like:
        return True
    return False
async def unlike(user_id:int, post_id:int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id  == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    like = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    if await has_liked(user_id=user_id, post_id=post_id, db=db) and like:
        db.delete(like)
        db.commit()
        return {'message':'unliked'}

async def count_likes_for_post(db: Session, post_id: int):
    return db.query(Like).filter_by(post_id=post_id).count()

async def count_comments(post_id:int, db: Session = Depends(get_db)):
    return db.query(Comment).filter_by(post_id=post_id).count()

async def follow_user(current_user, user_for_following, db: Session = Depends(get_db)):
    if user_for_following not in current_user.following:
        current_user.following.append(user_for_following)
        db.add(current_user)
        db.commit()
        return {'message': f'Successfully followed {user_for_following.username}'}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already followed')

async def unfollow(current_user:User, user_for_unfollowing:User, db: Session = Depends(get_db)):
    if user_for_unfollowing in current_user.following:
        current_user.following.remove(user_for_unfollowing)
        db.add(current_user)
        db.commit()
        return {'message':f'Succesfully unfollowed {user_for_unfollowing}'}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not followed')

async def has_followed(current_user:User, user_followed_id, db: Session= Depends(get_db)):
    user_followed = await check_user_by_id(user_id=user_followed_id, db=db)
    if user_followed in current_user.following:
        return True
    return False