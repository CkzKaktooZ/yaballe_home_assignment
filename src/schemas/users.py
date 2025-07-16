from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreateRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    password: str

class UserEditRequest(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    password: str | None = None

class UserBrief(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True
        
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


