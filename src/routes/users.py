from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.schemas import UserCreateRequest, UserOut
from src.models import User
from src.database import get_db
from src.schemas.auth import LoginRequest, TokenResponse
from src.services import hash_password
from src.services.auth import create_access_token, get_current_user, verify_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreateRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken.")
    
    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username, 
        hashed_password=hashed_pw
    ) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
    

# @router.post("/login")    
# def login(db: Session = Depends(get_db)):
#     pass


@router.get("/me", response_model=UserOut)
def get_current_user_data(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user




@router.delete("/{user_id}", response_model=UserOut)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_to_delete = db.query(User).filter(User.id == user_id).first()

    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    if user_to_delete.id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own account.")

    db.delete(user_to_delete)
    db.commit()
    return user_to_delete


@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": str(user.id)}  # put user ID in JWT
    token = create_access_token(data=token_data)
    return {"access_token": token, "token_type": "bearer"}

