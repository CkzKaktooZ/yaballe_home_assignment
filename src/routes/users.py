from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.schemas import UserSchemas, PostSchemas
from src.models import User
from src.database import get_db
from src.schemas.auth import LoginRequest, TokenResponse
from src.services import UserServices, AuthServices, PostServices
from src.utils import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserSchemas.UserOut)
def register(user: UserSchemas.UserCreateRequest, db: Session = Depends(get_db)):
    logger.info(
        f"Registration attempt | Email: '{user.email}' | Username: '{user.username}'"
    )
    user_with_username = UserServices.get_user_by_username(user.username, db)

    if user_with_username:
        logger.warning(f"Username taken: '{user.username}'")
        raise HTTPException(status_code=400, detail="Username already taken.")

    user_with_email = UserServices.get_user_by_email(user.email, db)

    if user_with_email:
        logger.warning(f"Email taken: '{user.email}'")
        raise HTTPException(status_code=400, detail="Email already taken.")

    new_user = UserServices.create_user(user, db)
    logger.info(
        f"User registered successfully | ID: {new_user.id} | Username: '{new_user.username}'"
    )
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for username: {request.username}")

    user = db.query(User).filter(User.username == request.username).first()

    if not user or not AuthServices.verify_password(
        request.password, user.hashed_password
    ):
        logger.warning(f"Failed login for username: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Login successful for user ID: {user.id}")
    token_data = {"sub": str(user.id)}  # put user ID in JWT
    token = AuthServices.create_access_token(data=token_data)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/", response_model=list[UserSchemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    logger.info("Fetching all users")
    users = UserServices.get_all_users(db)
    logger.info(f"Returned {len(users)} users")
    return users


@router.get("/me", response_model=UserSchemas.UserOut)
def get_current_user_data(current_user: User = Depends(AuthServices.get_current_user)):
    logger.info(f"Fetching data for current user ID: {current_user.id}")
    return current_user


@router.get("/search", response_model=list[UserSchemas.UserOut])
def search_users(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    logger.info(f"Searching users with query: '{q}'")
    users = UserServices.query_users(q, db)
    logger.info(f"Found {len(users)} users matching query: '{q}'")
    return users


@router.get("/{user_id}", response_model=UserSchemas.UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching user by ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User ID {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthServices.get_current_user),
):
    logger.info(
        f"Delete user attempt by user ID: {current_user.id} for user ID: {user_id}"
    )
    if user_id != current_user.id:
        logger.warning(
            f"Unauthorized delete attempt by user ID: {current_user.id} for user ID: {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized"
        )

    UserServices.delete_user_by_id(user_id, db)
    logger.info(f"User ID {user_id} deleted successfully")


@router.put("/me", response_model=UserSchemas.UserOut)
def edit_user(
    new_user_data: UserSchemas.UserEditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthServices.get_current_user),
):
    logger.info(f"Edit profile request for user ID: {current_user.id}")
    return UserServices.update_user_info(new_user_data, current_user.id, db)


@router.get("/{user_id}/posts", response_model=List[PostSchemas.PostOut])
def get_my_posts(
    user_id: int, q: Optional[str] = Query(None), db: Session = Depends(get_db)
):
    logger.info(f"Fetching posts for user ID: {user_id} with query: {q}")
    posts = PostServices.query_user_posts(user_id, db, query=q)
    logger.info(f"Found {len(posts)} posts for user ID: {user_id}")
    return posts
