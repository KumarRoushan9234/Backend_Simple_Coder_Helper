import bcrypt
import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from bson import ObjectId
from typing import Optional
from fastapi import APIRouter, HTTPException, Response, Request

def hash_password(password: str) -> str:
    """Hash the password and return it as a string."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')  # Ensure it's encoded if it's a string
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

ALGORITHM = "HS256"
def create_jwt_token(user_id: str):
    # Token expiration time
    expiration = datetime.utcnow() + timedelta(days=1)
    
    payload = {
        "sub": user_id,  # Use 'sub' for the user_id (standard claim for subject)
        "exp": expiration
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(authorization: str):
    """Verify the authorization token."""
    if not authorization:
        raise HTTPException(status_code=403, detail="Token is missing!")
    
    try:
        token = authorization.split(" ")[1]  # Extract the token after 'Bearer'
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except Exception:
        raise HTTPException(status_code=403, detail="Token is invalid!")

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # Return 'sub' claim as user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# MongoDB ObjectId serialization helper
def str_objectid(obj):
    """Helper function to serialize MongoDB ObjectId to string."""
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj