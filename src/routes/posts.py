from fastapi import APIRouter
from src.schemas import PostOut, VoteBase, VoteCount

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/")
def create_post():
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