from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.users import User
from src.services import AuthServices, PostServices
from src.schemas import PostSchemas, VoteSchemas
from src.utils.logger import logger

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostSchemas.PostOut)
def create_post(
    post_data: PostSchemas.PostCreate,
    current_user: User = Depends(AuthServices.get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(
        f"User {current_user.id} creating a new post titled '{post_data.title}'"
    )
    new_post = PostServices.create_post(post_data, current_user, db)
    logger.info(f"Post created with ID {new_post.id} by user {current_user.id}")
    return new_post


@router.get("/")
def get_all_posts(db: Session = Depends(get_db)):
    logger.info("Fetching all posts")
    posts = PostServices.get_all_posts(db)
    logger.info(f"Fetched {len(posts)} posts")
    return posts


@router.get("/search", response_model=list[PostSchemas.PostOut])
def search_posts(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    logger.info(f"Searching posts with query '{q}'")
    posts = PostServices.query_all_posts(q, db)
    logger.info(f"Search returned {len(posts)} posts")
    return posts


@router.get("/{post_id}", response_model=PostSchemas.PostOut)
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching post with ID {post_id}")
    post = PostServices.get_post_by_id(post_id, db)

    if not post:
        logger.warning(f"Post with ID {post_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    logger.info(f"Post with ID {post_id} retrieved successfully")
    return post


@router.put("/{post_id}")
def edit_post_by_id(
    post_id: int,
    post_data: PostSchemas.PostBase,
    current_user: User = Depends(AuthServices.get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"User {current_user.id} editing post {post_id}")
    updated_post = PostServices.edit_post_by_id(post_id, post_data, current_user.id, db)
    logger.info(f"Post {post_id} updated successfully by user {current_user.id}")
    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: User = Depends(AuthServices.get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"User {current_user.id} deleting post {post_id}")
    PostServices.delete_post_by_id(post_id, current_user, db)
    logger.info(f"Post {post_id} deleted successfully by user {current_user.id}")


@router.get("/{post_id}/votes", response_model=VoteSchemas.VoteCount)
def get_post_votes(post_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching votes for post {post_id}")
    votes = PostServices.get_vote_counts_for_post(post_id, db)
    logger.info(
        f"Post {post_id} has {votes['upvotes']} upvotes and {votes['downvotes']} downvotes"
    )
    return votes


@router.post("/{post_id}/vote", response_model=PostSchemas.PostOut)
def vote_on_post(
    post_id: int,
    vote: VoteSchemas.VoteRequest,
    current_user: User = Depends(AuthServices.get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"User {current_user.id} voting '{vote.vote}' on post {post_id}")
    post_response = PostServices.vote_on_post_service(
        post_id, vote.vote, current_user, db
    )
    logger.info(f"User {current_user.id} completed voting on post {post_id}")
    return post_response
