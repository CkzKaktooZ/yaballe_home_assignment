from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.schemas import UserSchemas, PostSchemas
from src.models import User
from src.database import get_db
from src.schemas.auth import LoginRequest, TokenResponse
from src.services import UserServices, AuthServices, PostServices

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserSchemas.UserOut)
def register(user: UserSchemas.UserCreateRequest, db: Session = Depends(get_db)):
    user_with_username = UserServices.get_user_by_username(user.username, db)
    
    if user_with_username:
        raise HTTPException(status_code=400, detail="Username already taken.")
    
    user_with_username = UserServices.get_user_by_email(user.email, db)

    if user_with_username:
        raise HTTPException(status_code=400, detail="Email already taken.")
    
    new_user = UserServices.create_user(user, db)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not AuthServices.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": str(user.id)}  # put user ID in JWT
    token = AuthServices.create_access_token(data=token_data)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/", response_model=list[UserSchemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    users = UserServices.get_all_users(db)
    return users


@router.get("/me", response_model=UserSchemas.UserOut)
def get_current_user_data(current_user: User = Depends(AuthServices.get_current_user)):
    return current_user


@router.get("/search", response_model=list[UserSchemas.UserOut])
def search_users(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    users = UserServices.query_users(q, db)
    return users

@router.get("/{user_id}", response_model=UserSchemas.UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(AuthServices.get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    UserServices.delete_user_by_id(user_id, db)

@router.put("/me", response_model=UserSchemas.UserOut)
def edit_user(new_user_data: UserSchemas.UserEditRequest, db: Session = Depends(get_db), current_user: User = Depends(AuthServices.get_current_user)):
    return UserServices.update_user_info(new_user_data, current_user.id, db)

@router.get("/{user_id}/posts", response_model=List[PostSchemas.PostOut])
def get_my_posts(user_id: int, q: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return PostServices.query_user_posts(user_id, db, query=q)






