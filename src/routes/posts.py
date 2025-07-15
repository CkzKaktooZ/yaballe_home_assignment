from fastapi import APIRouter
from src.schemas import PostOut, VoteBase, VoteCount

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostOut)
def create_post():
    pass

@router.get("/", response_model=[PostOut])
def get_all_posts():
    pass
    
@router.get("/{post_id}", response_model=PostOut)
def get_post():
    pass


@router.put("/{post_id}", response_model=PostOut)    
def edit_post():
    pass


@router.delete("/{post_id}", response_model=PostOut)    
def delete_post():
    pass

@router.post("/vote", response_model=VoteBase)
def vote():
    pass


@router.get("/votes/{post_id}", response_model=VoteCount)
def get_votes():
    pass