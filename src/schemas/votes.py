from pydantic import BaseModel
from enum import Enum

class VoteTypeEnum(str, Enum):
    upvote = "upvote"
    downvote = "downvote"


class VoteBase(BaseModel):
    post_id: int
    user_id: int
    vote_type: VoteTypeEnum


class VoteCount(BaseModel):
    upvotes: int
    downvotes: int