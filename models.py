from typing import Optional,List
import datetime
from pydantic import BaseModel, EmailStr, Field,constr
from bson.objectid import ObjectId

class UserBaseSchema(BaseModel):
    email: EmailStr = Field(...)
    name: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

class SignUpModel(BaseModel):
    email: EmailStr = Field(...)
    name: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "User Name",
                "username": "user",
                "password": "password",
            }
        }


class LoginModel(BaseModel):
    email: EmailStr = Field(...)
    password: constr(min_length=8) = Field(...)


class ModelSelection(BaseModel):
    model: str

class AskModel(BaseModel):
    user_input: str
