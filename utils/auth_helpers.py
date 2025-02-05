import bcrypt
import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY
from fastapi import HTTPException

def hash_password(password: str) -> str:
    """Hash the password and return it as a string."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')  # Ensure it's encoded if it's a string
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def create_jwt_token(user_id: str) -> str:
    """Create JWT token with 1 day expiration."""
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(days=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(authorization: str):
    """Verify the authorization token."""
    if not authorization:
        raise HTTPException(status_code=403, detail="Token is missing!")
    
    try:
        token = authorization.split(" ")[1]  # Extract the token after 'Bearer'
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token["user_id"]
    except Exception:
        raise HTTPException(status_code=403, detail="Token is invalid!")

def decode_jwt_token(token: str):
    """Decode JWT token and handle expired or invalid token errors."""
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired!")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token!")
