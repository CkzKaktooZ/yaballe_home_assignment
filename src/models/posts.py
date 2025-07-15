from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    author = relationship("User", back_populates="posts")
    votes = relationship("Vote", back_populates="post")
