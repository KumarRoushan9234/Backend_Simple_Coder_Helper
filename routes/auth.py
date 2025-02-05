from fastapi import APIRouter, HTTPException, Response, Request
from database import user_collection
from utils.auth_helpers import hash_password, verify_password, create_jwt_token, decode_jwt_token
from models import SignUpModel, LoginModel
from bson import ObjectId
from typing import Optional

router = APIRouter()

def success_response(message: str, data: Optional[dict] = None):
    return {"message": message, "success": True, "data": data}

def error_response(message: str):
    return {"message": message, "success": False}

@router.post("/signup")
async def signup(data: SignUpModel):
    if user_collection.find_one({"username": data.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(data.password)
    user_collection.insert_one({
        "email": data.email,
        "name": data.name,
        "username": data.username,
        "password": hashed_password,
    })
    return success_response("User created successfully!")

@router.post("/login")
async def login(response: Response, data: LoginModel):
    user = user_collection.find_one({"username": data.username})
    if user and verify_password(data.password, user["password"]):
        token = create_jwt_token(str(user["_id"]))
        response.set_cookie("access_token", token, httponly=True, max_age=86400)  # Store token in cookies
        return success_response("Login successful!")

    raise HTTPException(status_code=400, detail="Invalid username or password")

# @router.get("/check-auth")
# async def check_auth(request: Request):
#     token = request.cookies.get("access_token")  # Retrieve token from cookies
#     if not token:
#         raise HTTPException(status_code=403, detail="Token is missing")

#     try:
#         decoded_token = decode_jwt_token(token)  # Decode and verify the token
#         user = user_collection.find_one({"_id": ObjectId(decoded_token["user_id"])})
#         if not user:
#             raise HTTPException(status_code=403, detail="User not found")
#         return success_response("User authenticated", {"username": user["username"]})
#     except:
#         raise HTTPException(status_code=403, detail="Invalid token")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")  # Delete token cookie
    return success_response("User logged out successfully!")
