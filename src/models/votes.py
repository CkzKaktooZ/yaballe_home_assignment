from sqlalchemy import Column, Integer, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database import Base
import enum


class VoteType(str, enum.Enum):
    upvote = "upvote"
    downvote = "downvote"


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="unique_vote"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    vote_type = Column(Enum(VoteType), nullable=False)

    user = relationship("User", back_populates="votes")
    post = relationship("Post", back_populates="votes")
