from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime, timezone


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    author = relationship("User", back_populates="posts")
    votes = relationship("Vote", back_populates="post", cascade="all, delete")

    @property
    def upvotes(self):
        return len([v for v in self.votes if v.vote_type == "upvote"])

    @property
    def downvotes(self):
        return len([v for v in self.votes if v.vote_type == "downvote"])
