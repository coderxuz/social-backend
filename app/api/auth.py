from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Header,
    responses,
    Request,
    Depends,
)
from datetime import timedelta, datetime
from app.database import get_db
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas import SignUser, Auth, Login, Reset, Message, Refresh, Myself
import hashlib
from app.models import User
from app.utils import check_user_by_username, verify_token, get_user_from_token
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["AUTH"])

SECRET_KEY = "fe89708897e427a05eb58670e36d9fbfc7da76266081cc62c0064f347dd1e5c7"

ACCESS_TOKEN_EXPIRES_MINUTES = 30
REFRESH_TOKEN_EXPIRES_DAYS = 1
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/authorize")


def create_tokens(username: str) -> list[str]:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS)
    access_token = jwt.encode(
        {"sub": username, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    refresh_token = jwt.encode(
        {"sub": username, "exp": datetime.utcnow() + refresh_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return [access_token, refresh_token]


def hash_password(password: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode("utf-8"))
    return md5_hash.hexdigest()


def verify_password(db_user_pass: str, login_user_pass: str) -> bool:
    return db_user_pass == hash_password(login_user_pass)


@router.post("/sign-up", response_model=Auth, status_code=status.HTTP_201_CREATED)
async def create_user(user: SignUser, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username or email already exist",
        )
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hash_password(user.password),
        username=user.username,
        user_img=None,
    )
    db.add(new_user)
    tokens = create_tokens(username=user.username)
    access_token = tokens[0]
    refresh_token = tokens[1]
    db.commit()
    return {
        "message": "user successfully created",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/login", response_model=Auth, status_code=status.HTTP_200_OK)
async def login(user: Login, db: Session = Depends(get_db)):
    db_user = check_user_by_username(user.username, db)
    if not verify_password(db_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="password incorrect"
        )
    tokens = create_tokens(username=user.username)
    access_token = tokens[0]
    refresh_token = tokens[1]
    return {
        "message": "login success",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.get(
    "/refresh", status_code=status.HTTP_200_OK,response_model=Refresh, dependencies=[Depends(oauth2_scheme)]
)
async def refresh(request: Request):
    payload = verify_token(request)
    if payload:
        tokens = create_tokens(payload["sub"])
        access_token = tokens[0]
        
        
        return {"accessToken": access_token, "token_type": "bearer"}


@router.post("/authorize")
async def authorize(
    user: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
):
    db_user = check_user_by_username(user.username, db)
    if not verify_password(db_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="password incorrect"
        )
    tokens = create_tokens(username=user.username)
    access_token = tokens[0]
    refresh_token = tokens[1]
    return {
        "message": "login success",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/reset-pass", response_model=Message)
async def reset(user: Reset, db: Session = Depends(get_db)):
    db_user = check_user_by_username(user_username=user.username, db=db)
    if user.code == 1234:
        db_user.password = hash_password(user.new_pass)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {'message':'password successfully changed'}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="code incorrect"
    )
@router.get('/me', dependencies=[Depends(oauth2_scheme)], response_model=Myself)
async def myself(request:Request,db: Session = Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    user_data = {
        'id':db_user.id,
        'first_name':db_user.first_name if db_user.first_name else None,
        'last_name':db_user.last_name,
        'email':db_user.email,
        'username':db_user.username,
        'followers':db_user.follower_count,
        'followings':db_user.followings_count,
        'user_img':f"{request.url.scheme}://{request.url.netloc}/image/{db_user.user_img}" if db_user.user_img else None
    }
    return user_data

@router.get('/users')
async def users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    users_list = []
    for user in users:
        users_list.append(
            {
                'username':user.username
            }
        )
    return users_list