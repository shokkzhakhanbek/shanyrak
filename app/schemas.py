from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    phone: str
    password: str
    name: str
    city: str


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    city: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    phone: str
    name: str
    city: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str



class ShanyrakCreate(BaseModel):
    type: str
    price: float
    address: str
    area: float
    rooms_count: int
    description: str


class ShanyrakUpdate(BaseModel):
    type: Optional[str] = None
    price: Optional[float] = None
    address: Optional[str] = None
    area: Optional[float] = None
    rooms_count: Optional[int] = None
    description: Optional[str] = None


class ShanyrakResponse(BaseModel):
    id: int
    type: str
    price: float
    address: str
    area: float
    rooms_count: int
    description: str
    user_id: int
    total_comments: int = 0

    class Config:
        from_attributes = True


class ShanyrakCreateResponse(BaseModel):
    id: int


# ─── Comments ────────────────────────────────────────

class CommentCreate(BaseModel):
    content: str


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author_id: int

    class Config:
        from_attributes = True


class CommentsListResponse(BaseModel):
    comments: list[CommentResponse]