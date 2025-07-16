from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.users import User
from src.services import AuthServices, PostServices
from src.schemas import PostSchemas, VoteSchemas

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostSchemas.PostOut)
def create_post(post_data: PostSchemas.PostCreate, current_user: User = Depends(AuthServices.get_current_user), db: Session = Depends(get_db)):
    new_post = PostServices.create_post(post_data, current_user, db)
    return new_post


@router.get("/")
def get_all_posts(db: Session = Depends(get_db)):
    return PostServices.get_all_posts(db)
    

@router.get("/search", response_model=list[PostSchemas.PostOut])
def search_posts(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return PostServices.query_all_posts(q, db)


@router.get("/{post_id}", response_model=PostSchemas.PostOut)
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    post = PostServices.get_post_by_id(post_id, db)
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    return post


@router.put("/{post_id}")    
def edit_post_by_id(post_id: int, post_data: PostSchemas.PostBase, current_user: User = Depends(AuthServices.get_current_user), db: Session = Depends(get_db)):
    return PostServices.edit_post_by_id(post_id, post_data, current_user.id, db)


@router.delete("/{post_id}")    
def delete_post(post_id: int, current_user: User = Depends(AuthServices.get_current_user), db: Session = Depends(get_db)):
    PostServices.delete_post_by_id(post_id, current_user, db)


@router.get("/{post_id}/votes", response_model=VoteSchemas.VoteCount)
def get_post_votes(post_id: int, db: Session = Depends(get_db)):
    return PostServices.get_vote_counts_for_post(post_id, db)

@router.post("/{post_id}/vote", response_model=PostSchemas.PostOut)
def vote_on_post(post_id: int, vote: VoteSchemas.VoteTypeEnum, current_user: User = Depends(AuthServices.get_current_user), db: Session = Depends(get_db)):
    return PostServices.vote_on_post_service(post_id, vote, current_user, db)
