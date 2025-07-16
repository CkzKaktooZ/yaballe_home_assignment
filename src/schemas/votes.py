from pydantic import BaseModel
from enum import Enum


class VoteTypeEnum(str, Enum):
    upvote = "upvote"
    downvote = "downvote"


class VoteRequest(BaseModel):
    vote: VoteTypeEnum


class VoteCount(BaseModel):
    upvotes: int
    downvotes: int
