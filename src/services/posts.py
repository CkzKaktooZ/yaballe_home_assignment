from typing import List, Optional
from sqlalchemy import or_
from src.schemas import PostSchemas
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import User, Post, Vote
from src.schemas import UserSchemas, VoteSchemas
from . import AuthServices

def create_post(post_data: PostSchemas.PostCreate, user: User, db: Session) -> Post:
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        author_id=user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def get_all_posts(db: Session) -> list[Post]:
    return db.query(Post).order_by(Post.created_at.desc()).all()


def get_post_by_id(post_id: int, db: Session) -> Post:
    return db.query(Post).filter(Post.id == post_id).first()


def delete_post_by_id(post_id: int, current_user: User, db: Session):
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post.")
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    
    db.delete(post)
    db.commit()

def get_vote_counts_for_post(post_id: int, db: Session) -> VoteSchemas.VoteCount:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    upvotes = db.query(Vote).filter(Vote.post_id == post_id, Vote.vote_type == VoteSchemas.VoteTypeEnum.upvote).count()
    downvotes = db.query(Vote).filter(Vote.post_id == post_id, Vote.vote_type == VoteSchemas.VoteTypeEnum.downvote).count()

    return {"upvotes": upvotes, "downvotes": downvotes}

def get_user_vote_on_post(post_id: int, user_id: int, db: Session):
    post = get_post_by_id(post_id, db)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    return db.query(Vote).filter(
        Vote.post_id == post_id,
        Vote.user_id == user_id
    ).first()

    
def vote_on_post_service(post_id: int, vote: VoteSchemas.VoteTypeEnum, current_user: User, db: Session):
    post = get_post_by_id(post_id, db)
    existing_vote = get_user_vote_on_post(post_id, current_user.id, db)

    if existing_vote:
        if existing_vote.vote_type != vote:
            existing_vote.vote_type = vote
            db.commit()
    else:
        new_vote = Vote(
            post_id=post_id,
            user_id=current_user.id,
            vote_type=vote
        )
        db.add(new_vote)
        db.commit()

    upvotes = db.query(Vote).filter(Vote.post_id == post_id, Vote.vote_type == VoteSchemas.VoteTypeEnum.upvote).count()
    downvotes = db.query(Vote).filter(Vote.post_id == post_id, Vote.vote_type == VoteSchemas.VoteTypeEnum.downvote).count()

    post_response = PostSchemas.PostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        author=post.author,
        upvotes=upvotes,
        downvotes=downvotes,
        created_at=post.created_at
    )
    return post_response
        
def edit_post_by_id(post_id: int, post_data: PostSchemas.PostBase, current_user_id: int, db: Session) -> Post:
    post = get_post_by_id(post_id, db)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this post")

    post.title = post_data.title
    post.content = post_data.content

    db.commit()
    db.refresh(post)

    return post

def query_all_posts(q: str, db: Session) -> List[PostSchemas.PostOut]:
    return db.query(Post).filter(
        or_(
            Post.title.ilike(f"%{q}%"),
            Post.content.ilike(f"%{q}%"),
        )
    ).all()

def query_user_posts(user_id: int, db: Session, query: Optional[str] = None) -> List[Post]:
    q = db.query(Post).filter(Post.author_id == user_id)
    
    if query:
        q = q.filter(
            or_(
                Post.title.ilike(f"%{query}%"),
                Post.content.ilike(f"%{query}%")
            )
        )

    return q.order_by(Post.created_at.desc()).all()