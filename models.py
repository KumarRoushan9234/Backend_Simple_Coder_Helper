from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, constr

# Base user model
class UserBaseSchema(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    name: str = Field(..., example="User Name")
    username: str = Field(..., example="user")
    password: str = Field(..., example="password")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# SignUpModel for registration
class SignUpModel(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    name: str = Field(..., example="User Name")
    username: str = Field(..., example="user")
    password: str = Field(..., example="password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "User Name",
                "username": "user",
                "password": "password",
            }
        }

# Login model
class LoginModel(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: constr(min_length=8) = Field(..., example="password")

# Model selection
class ModelSelection(BaseModel):
    model: str

# User input for chat
class AskModel(BaseModel):
    user_input: str

# Chat history structure
class ChatHistoryModel(BaseModel):
    user_message: str
    system_response: str
    timestamp: datetime

# User model with chat history and selected model
class UserModel(BaseModel):
    user_id: str
    selected_model: Optional[str]
    chat_history: Optional[List[ChatHistoryModel]] = []

    class Config:
        from_attributes = True

# For storing user selection of a model
class UserSelection(BaseModel):
    user_id: str
    selected_model: str
