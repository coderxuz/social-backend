from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class SignUser(BaseModel):
    first_name: str
    last_name: Optional[str]
    email: EmailStr
    password: str
    username:str
class Auth(BaseModel):
    message: str
    access_token: str
    refresh_token: str
class Login(BaseModel):
    username:str
    password:str
class Refresh(BaseModel):
    access_token:str
    token_typ:str='bearer'
class Reset(BaseModel):
    username:str
    code:int
    new_pass:str    
class ImageResponse(BaseModel):
    image_id:int
class PostCreate(BaseModel):
    text:str
    image_id:Optional[int]
class Message(BaseModel):
    message:str
class PostsGet(BaseModel):
    id: int
    image: Optional[str]
    text: str   
    this_user: bool
    has_liked: bool
    likes: int
    comments: int