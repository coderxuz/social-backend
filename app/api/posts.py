from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.auth import oauth2_scheme
from app.database import get_db
from app.schemas import PostCreate, Message, PostsGet, LikeUnlike
from app.utils import get_user_from_token, has_liked, count_likes_for_post, like_post, count_comments, unlike
from app.models import Post, Image
from typing import List

router = APIRouter(prefix='/posts', tags=['POSTS'])
@router.post('/upload', dependencies=[Depends(oauth2_scheme)], response_model=Message)
async def post(post:PostCreate,request:Request,db:Session = Depends(get_db)):

    db_user = await get_user_from_token(request=request, database=db)
    if post.image_id:
        db_image = db.query(Image).filter(Image.id == post.image_id).first()
        if not db_image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='image not uploaded and not found from database')
        new_post = Post(text = post.text, image_id = post.image_id, user=db_user)
        db.add(new_post)
        db.commit()
        return {'message':'post successfully created'}
    new_post = Post(text = post.text, user=db_user)
    db.add(new_post)
    db.commit()
    return {'message':'post successfully created'}

@router.get('/',dependencies=[Depends(oauth2_scheme)], response_model=List[PostsGet])
async def posts(request:Request, db: Session = Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db) 
    random_posts = (
        db.query(Post).order_by(func.random()).limit(10).all()
    )
    posts_list = []
    for item in random_posts:
        if item.image_id:
            if item.user.user_img:
                posts_list.append(
                {
                    'id':item.id,
                    'username':item.user.username,
                    'user_image':f"{request.url.scheme}://{request.url.netloc}/image/{item.user.user_img}",
                    'image':f"{request.url.scheme}://{request.url.netloc}/image/{item.image_id}",
                    'text':item.text,
                    'this_user':db_user.id == item.user_id,
                    'has_liked':await has_liked(user_id=db_user.id, post_id=item.id, db=db),
                    'likes': await count_likes_for_post(post_id=item.id, db=db),
                    'comments':await count_comments(post_id=item.id, db=db)
                }
            )
            else:
                posts_list.append(
                {
                    'id':item.id,
                    'username':item.user.username,
                    'user_image':None,
                    'image':f"{request.url.scheme}://{request.url.netloc}/image/{item.image_id}",
                    'text':item.text,
                    'this_user':db_user.id == item.user_id,
                    'has_liked':await has_liked(user_id=db_user.id, post_id=item.id, db=db),
                    'likes': await count_likes_for_post(post_id=item.id, db=db),
                    'comments':await count_comments(post_id=item.id, db=db)
                }
            )
        else:
            if item.user.user_img:
                posts_list.append(
                {
                    'id':item.id,
                    'image':None,
                    'username':item.user.username,
                    'user_image':f"{request.url.scheme}://{request.url.netloc}/image/{item.image_id}",
                    'text':item.text,
                    'this_user':db_user.id == item.user_id,
                    'has_liked':await has_liked(user_id=db_user.id, post_id=item.id, db=db),
                    'likes': await count_likes_for_post(post_id=item.id, db=db),
                    'comments':await count_comments(post_id=item.id, db=db)
                }
            )
            else:
              posts_list.append(
                {
                    'id':item.id,
                    'image':None,
                    'username':item.user.username,
                    'user_image':None,
                    'text':item.text,
                    'this_user':db_user.id == item.user_id,
                    'has_liked':await has_liked(user_id=db_user.id, post_id=item.id, db=db),
                    'likes': await count_likes_for_post(post_id=item.id, db=db),
                    'comments':await count_comments(post_id=item.id, db=db)
                }
              )
    return posts_list
@router.post('/like', response_model=Message, dependencies=[Depends(oauth2_scheme)])
async def like(post_id:LikeUnlike,request:Request, db: Session = Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    unlike_post = await unlike(user_id=db_user.id, post_id=post_id.post_id, db=db)
    if not unlike_post:
        like_the_post = await like_post(user_id=db_user.id, post_id=post_id.post_id, db=db)
        return like_the_post
    return unlike_post