from fastapi import Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import User
from src.schemas import UserSchemas
from src.utils import logger
from . import AuthServices


def get_user_by_email(email: str, db: Session) -> User:
    logger.debug(f"Fetching user by email: {email}")
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(username: str, db: Session) -> User:
    logger.debug(f"Fetching user by username: {username}")
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(id: int, db: Session) -> User:
    logger.debug(f"Fetching user by id: {id}")
    return db.query(User).filter(User.id == id).first()


def get_all_users(db: Session) -> list[User]:
    logger.debug("Fetching all users")
    return db.query(User).all()


def query_users(q: str, db: Session) -> list[User]:
    logger.debug(f"Querying users with search term: {q}")
    return (
        db.query(User)
        .filter(
            or_(
                User.username.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%"),
            )
        )
        .all()
    )


def delete_user_by_id(user_id: int, db: Session):
    logger.info(f"Deleting user with id: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.warning(f"Delete failed: User with id {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()
    logger.info(f"User with id {user_id} successfully deleted")


def create_user(user: UserSchemas.UserCreateRequest, db: Session):
    logger.info(
        f"Creating new user with username: {user.username}, email: {user.email}"
    )
    hashed_pw = AuthServices.hash_password(user.password)
    new_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        hashed_password=hashed_pw,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User created with id: {new_user.id}")
    return new_user


def update_user_info(
    user_new_data: UserSchemas.UserEditRequest, user_id: int, db: Session
):
    logger.info(f"Updating user info for user id: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.warning(f"Update failed: User with id {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_new_data.username is not None:
        logger.debug(f"Updating username to: {user_new_data.username}")
        user.username = user_new_data.username

    if user_new_data.email is not None:
        logger.debug(f"Updating email to: {user_new_data.email}")
        user.email = user_new_data.email

    if user_new_data.first_name is not None:
        logger.debug(f"Updating first name to: {user_new_data.first_name}")
        user.first_name = user_new_data.first_name

    if user_new_data.last_name is not None:
        logger.debug(f"Updating last name to: {user_new_data.last_name}")
        user.last_name = user_new_data.last_name

    if user_new_data.password is not None:
        logger.debug(f"Updating password for user id: {user_id}")
        user.hashed_password = AuthServices.hash_password(user_new_data.password)

    db.commit()
    db.refresh(user)
    logger.info(f"User info updated successfully for user id: {user_id}")
    return user
