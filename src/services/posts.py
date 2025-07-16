from typing import List, Optional
from sqlalchemy import or_
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.schemas import PostSchemas, VoteSchemas
from src.models import User, Post, Vote
from src.utils import logger


def create_post(post_data: PostSchemas.PostCreate, user: User, db: Session) -> Post:
    logger.info(
        f"Creating post titled '{post_data.title}' for user {user.username} (id {user.id})"
    )
    new_post = Post(title=post_data.title, content=post_data.content, author_id=user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    logger.info(f"Post created with id {new_post.id}")
    return new_post


def get_all_posts(db: Session) -> list[Post]:
    logger.debug("Fetching all posts ordered by creation date")
    return db.query(Post).order_by(Post.created_at.desc()).all()


def get_post_by_id(post_id: int, db: Session) -> Post:
    logger.debug(f"Fetching post by id {post_id}")
    return db.query(Post).filter(Post.id == post_id).first()


def delete_post_by_id(post_id: int, current_user: User, db: Session):
    logger.info(
        f"User {current_user.username} (id {current_user.id}) attempting to delete post {post_id}"
    )
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        logger.warning(f"Post {post_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    if post.author_id != current_user.id:
        logger.warning(
            f"User {current_user.id} not authorized to delete post {post_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post.",
        )

    db.delete(post)
    db.commit()
    logger.info(f"Post {post_id} deleted successfully")


def get_vote_counts_for_post(post_id: int, db: Session) -> VoteSchemas.VoteCount:
    logger.debug(f"Getting vote counts for post {post_id}")
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        logger.warning(f"Post {post_id} not found for vote count")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    upvotes = (
        db.query(Vote)
        .filter(
            Vote.post_id == post_id, Vote.vote_type == VoteSchemas.VoteTypeEnum.upvote
        )
        .count()
    )
    downvotes = (
        db.query(Vote)
        .filter(
            Vote.post_id == post_id, Vote.vote_type == VoteSchemas.VoteTypeEnum.downvote
        )
        .count()
    )

    logger.debug(f"Post {post_id} has {upvotes} upvotes and {downvotes} downvotes")
    return {"upvotes": upvotes, "downvotes": downvotes}


def get_user_vote_on_post(post_id: int, user_id: int, db: Session):
    logger.debug(f"Getting vote of user {user_id} on post {post_id}")
    post = get_post_by_id(post_id, db)

    if not post:
        logger.warning(f"Post {post_id} not found while fetching user vote")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return (
        db.query(Vote).filter(Vote.post_id == post_id, Vote.user_id == user_id).first()
    )


def vote_on_post_service(
    post_id: int, vote: VoteSchemas.VoteTypeEnum, current_user: User, db: Session
):
    logger.info(
        f"User {current_user.username} (id {current_user.id}) voting '{vote.value}' on post {post_id}"
    )
    post = get_post_by_id(post_id, db)

    if not post:
        logger.warning(f"Post {post_id} not found for voting")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    existing_vote = get_user_vote_on_post(post_id, current_user.id, db)

    if existing_vote:
        if existing_vote.vote_type != vote:
            logger.info(
                f"Updating vote from '{existing_vote.vote_type.value}' to '{vote.value}' for user {current_user.id} on post {post_id}"
            )
            existing_vote.vote_type = vote
            db.commit()
        else:
            logger.debug(
                f"User {current_user.id} already voted '{vote.value}' on post {post_id}, no change"
            )
    else:
        logger.info(
            f"Adding new vote '{vote.value}' for user {current_user.id} on post {post_id}"
        )
        new_vote = Vote(post_id=post_id, user_id=current_user.id, vote_type=vote)
        db.add(new_vote)
        db.commit()

    upvotes = (
        db.query(Vote)
        .filter(
            Vote.post_id == post_id, Vote.vote_type == VoteSchemas.VoteTypeEnum.upvote
        )
        .count()
    )
    downvotes = (
        db.query(Vote)
        .filter(
            Vote.post_id == post_id, Vote.vote_type == VoteSchemas.VoteTypeEnum.downvote
        )
        .count()
    )

    logger.debug(f"Post {post_id} now has {upvotes} upvotes and {downvotes} downvotes")

    post_response = PostSchemas.PostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        author=post.author,
        upvotes=upvotes,
        downvotes=downvotes,
        created_at=post.created_at,
    )
    return post_response


def edit_post_by_id(
    post_id: int, post_data: PostSchemas.PostBase, current_user_id: int, db: Session
) -> Post:
    logger.info(f"User {current_user_id} editing post {post_id}")
    post = get_post_by_id(post_id, db)

    if not post:
        logger.warning(f"Post {post_id} not found for editing")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.author_id != current_user_id:
        logger.warning(f"User {current_user_id} not authorized to edit post {post_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this post",
        )

    post.title = post_data.title
    post.content = post_data.content

    db.commit()
    db.refresh(post)

    logger.info(f"Post {post_id} edited successfully")
    return post


def query_all_posts(q: str, db: Session) -> List[PostSchemas.PostOut]:
    logger.debug(f"Querying all posts with search term '{q}'")
    return (
        db.query(Post)
        .filter(
            or_(
                Post.title.ilike(f"%{q}%"),
                Post.content.ilike(f"%{q}%"),
            )
        )
        .all()
    )


def query_user_posts(
    user_id: int, db: Session, query: Optional[str] = None
) -> List[Post]:
    logger.debug(f"Querying posts for user {user_id} with search term '{query}'")
    q = db.query(Post).filter(Post.author_id == user_id)

    if query:
        q = q.filter(
            or_(Post.title.ilike(f"%{query}%"), Post.content.ilike(f"%{query}%"))
        )

    return q.order_by(Post.created_at.desc()).all()
