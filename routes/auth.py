import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from typing import Optional
from config import SECRET_KEY
from database import user_collection
from models import SignUpModel, LoginModel, UpdateUserModel
from utils.auth_helpers import (
    hash_password,
    verify_password,
    create_jwt_token,
    decode_jwt_token,
    str_objectid,
)

router = APIRouter()


# Helper functions for success & error responses
def success_response(message: str, data: Optional[dict] = None):
    return {"message": message, "success": True, "data": data}


def error_response(message: str):
    return {"message": message, "success": False, "data": None}


# ----------------------- SIGNUP -----------------------
@router.post("/signup")
async def signup(data: SignUpModel):
    if user_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail=error_response("Email already exists"))
    
    if user_collection.find_one({"username": data.username}):
        raise HTTPException(status_code=400, detail=error_response("Username already taken"))

    hashed_password = hash_password(data.password)
    user = {
        "email": data.email,
        "name": data.name,
        "username": data.username,
        "password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    user_collection.insert_one(user)
    return success_response("User created successfully!")


# ----------------------- LOGIN -----------------------
@router.post("/login")
async def login(response: Response, data: LoginModel):
    user = user_collection.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=400, detail=error_response("Invalid email or password"))

    token = create_jwt_token(str(user["_id"]))

    # Secure cookie storage
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=86400,
    )

    return success_response("Login successful!", {"token": token})


# ----------------------- LOGOUT -----------------------
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return success_response("User logged out successfully!")


# ----------------------- AUTH CHECK -----------------------
@router.get("/me")
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    
    if not token:
        return JSONResponse(status_code=401, content=error_response("Not authenticated"))

    user_id = decode_jwt_token(token)
    
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return JSONResponse(status_code=401, content=error_response("Invalid token"))

    user = user_collection.find_one({"_id": user_id}, {"password": 0})  # Exclude password
    
    if not user:
        return JSONResponse(status_code=401, content=error_response("User not found"))

    # print("User Data:", user)  # Debugging

    return success_response("User authenticated", {
        "id": str(user["_id"]),
        "name": user.get("name", "Unknown"),
        "email": user["email"],
        "username": user["username"],
    })


# ----------------------- UPDATE USER -----------------------
@router.put("/update-user")
async def update_user(request: Request, data: UpdateUserModel):
    """
    Update user details such as name or username.
    Authentication required (JWT token in cookies).
    """
    token = request.cookies.get("access_token")
    
    if not token:
        return JSONResponse(status_code=401, content={"message": "Not authenticated", "success": False})

    user_id = decode_jwt_token(token)
    
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return JSONResponse(status_code=401, content={"message": "Invalid token", "success": False})

    user = user_collection.find_one({"_id": user_id})

    if not user:
        return JSONResponse(status_code=404, content={"message": "User not found", "success": False})

    update_data = {}

    # if "password" in data:
    #     hashed_password = hash_password(data["password"])
    #     update_data["password"] = hashed_password

    # Check for username change and ensure uniqueness
    if data.username:
        existing_user = user_collection.find_one({"username": data.username})
        if existing_user and str(existing_user["_id"]) != str(user_id):
            raise HTTPException(status_code=400, detail="Username already taken")
        update_data["username"] = data.username

    # Check for name update
    if data.name:
        update_data["name"] = data.name

    if not update_data:
        return JSONResponse(status_code=400, content={"message": "No valid fields to update", "success": False})

    # Update the user document
    update_data["updated_at"] = datetime.utcnow()
    user_collection.update_one({"_id": user_id}, {"$set": update_data})

    return {"message": "User updated successfully", "success": True}