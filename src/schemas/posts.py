from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .users import UserBrief


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostOut(PostBase):
    id: int
    created_at: datetime
    author: UserBrief
    upvotes: int = 0
    downvotes: int = 0
    model_config = ConfigDict(from_attributes=True)
