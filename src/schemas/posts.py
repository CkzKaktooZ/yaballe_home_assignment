from pydantic import BaseModel
from datetime import datetime
from .users import UserOut

class PostBase(BaseModel):
    title: str
    content: str


class PostOut(PostBase):
    id: int
    created_at: datetime
    author: UserOut
    upvotes: int
    downvotes: int

    class Config:
        orm_mode = True