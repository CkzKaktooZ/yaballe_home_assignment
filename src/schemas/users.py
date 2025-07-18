from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, constr
from datetime import datetime


class UserCreateRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    password: str


class UserEditRequest(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserBrief(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    model_config = ConfigDict(from_attributes=True)
