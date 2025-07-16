from typing import Any
from fastapi import APIRouter, Depends
from src.models.users import User
from src.schemas import PostOut, VoteBase, VoteCount
from src.services.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/")
def create_post(post_data: Any, current_user: User = Depends(get_current_user)):
    return 

@router.get("/")
def get_all_posts():
    pass
    
@router.get("/{post_id}")
def get_post():
    pass


@router.put("/{post_id}")    
def edit_post():
    pass


@router.delete("/{post_id}")    
def delete_post():
    pass

@router.post("/vote")
def vote():
    pass


@router.get("/votes/{post_id}")
def get_votes():
    pass