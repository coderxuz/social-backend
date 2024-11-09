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
from app.schemas import CommentData, Message, CommentGet
from app.utils import get_user_from_token, new_comment, has_followed
from app.models import Post, Comment

router = APIRouter(prefix="/comments", tags=["COMMENTS"])


@router.post("", dependencies=[Depends(oauth2_scheme)], response_model=Message)
async def comment(data: CommentData, request: Request, db: Session = Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    db_post = db.query(Post).filter(Post.id == data.post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )
    new_comment_data = await new_comment(
        content=data.content, current_user=db_user, post=db_post, database=db
    )
    return new_comment_data


@router.get(
    "/{id}", dependencies=[Depends(oauth2_scheme)], response_model=list[CommentGet]
)
async def get_comments(id: int, request: Request, db: Session = Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    db_post = db.query(Post).filter(Post.id == id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )
    comments = db.query(Comment).filter(Comment.post_id == db_post.id).all()
    comments_list = []
    for comment in comments:
        comments_list.append(
            {
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at,
                "this_user": True if comment.user_id == db_user.id else False,
                "username":comment.user.username,
                'user_img':f"{request.url.scheme}://{request.url.netloc}/image/{comment.user.user_img}" if comment.user.user_img else None,
                "has_followed":await has_followed(current_user=db_user, db=db, user_followed_id=comment.user.id)
            }
        )
    return comments_list


@router.delete("/{id}", dependencies=[Depends(oauth2_scheme)], response_model=Message)
async def del_comment(id: int, request: Request, db: Session = Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    comment = db.query(Comment).filter(Comment.id == id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
        )
    if comment not in db_user.comments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="this is not your comment"
        )
    db.delete(comment)
    db.commit()
    return {'message':'comment successfully deleted'}

