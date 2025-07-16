from fastapi import Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import User
from src.schemas import UserSchemas
from . import AuthServices


def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(username: str, db: Session) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(id: int, db: Session) -> User:
    return db.query(User).filter(User.id == id).first()


def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()


def query_users(q: str, db: Session) -> list[User]:
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
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()


def create_user(user: UserSchemas.UserCreateRequest, db: Session):
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
    return new_user


def update_user_info(
    user_new_data: UserSchemas.UserEditRequest, user_id: int, db: Session
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_new_data.username is not None:
        user.username = user_new_data.username

    if user_new_data.email is not None:
        user.email = user_new_data.email

    if user_new_data.first_name is not None:
        user.first_name = user_new_data.first_name

    if user_new_data.last_name is not None:
        user.last_name = user_new_data.last_name

    if user_new_data.password is not None:
        user.hashed_password = AuthServices.hash_password(user_new_data.password)

    db.commit()
    db.refresh(user)
    return user
