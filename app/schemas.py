from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner: UserResponse

    class Config:
        orm_mode = True


class PostResponse(BaseModel):
    Post: Post
    likes: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class Rate(BaseModel):
    post_id: int
    dir: Literal[0, 1]
