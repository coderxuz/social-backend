from fastapi import HTTPException, status, Request, Depends
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User
from typing import Optional, Dict, Any
from jose import jwt, JWTError

def check_user_by_email(
    user_email: str, db: Session = Depends(get_db)
) -> Optional[User]:
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    return db_user


def check_user_by_username(
    user_username: str, db: Session = Depends(get_db)
) -> Optional[User]:
    db_user = db.query(User).filter(User.username == user_username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
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
