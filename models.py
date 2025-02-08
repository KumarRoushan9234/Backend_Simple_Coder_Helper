from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, constr


class UserBaseSchema(BaseModel):
    email: EmailStr = Field(...)
    name: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Updated for Pydantic v2


class SignUpModel(BaseModel):
    email: EmailStr = Field(...)
    name: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {  # Updated for Pydantic v2
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
