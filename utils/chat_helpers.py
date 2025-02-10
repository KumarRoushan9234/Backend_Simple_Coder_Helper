from datetime import datetime
from database import conversation_collection, user_collection
from fastapi import  HTTPException, Request
from utils.auth_helpers import  decode_jwt_token
from bson import ObjectId

# global current_user

# ----------------- Get Current User -----------------
def get_CurrentUser(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id_str = decode_jwt_token(token)
    try:
        user_id = ObjectId(user_id_str)
        user = user_collection.find_one({"_id": user_id}, {"password": 0})
        if not user:
            print("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        print("User authenticated", {
            "id": str(user["_id"]),
            "name": user.get("name", "Unknown"),
            "email": user["email"],
            "username": user["username"],
            "selected_model": user.get("selected_model", "None")
        })
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user
    except Exception:
        print("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

# ----------------- Update Chat History -----------------
def update_chat_history(user_message: str, system_response: str, user_id: str, model: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation_entry = {
        "user": user_message,
        "assistant": system_response,
        "model": model,
        "timestamp": timestamp
    }

    conversation_collection.update_one(
        {"user_id": str(user_id)},  # Ensure user_id is a string
        {"$push": {"conversation": conversation_entry}},
        upsert=True
    )

    user_collection.update_one(
        {"_id": ObjectId(user_id)},  # Convert back to ObjectId for query
        {"$set": {"selected_model": model}},
        upsert=True
    )

# ----------------- Get Recent Conversation -----------------
def get_recent_conversation(user_id: str) -> list:
    doc = conversation_collection.find_one({"user_id": str(user_id)})
    if doc and "conversation" in doc:
        return doc["conversation"][-5:]
    return []