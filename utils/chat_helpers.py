from datetime import datetime
from database import conversation_collection, user_collection

def load_selected_model(user_id):
    user_data = user_collection.find_one({"_id": user_id})
    return user_data.get("selected_model") if user_data else None

def update_chat_history(user_message, system_response, user_id, model):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation_collection.insert_one({
        "user_id": user_id,
        "user": user_message,
        "assistant": system_response,
        "model": model,
        "timestamp": timestamp
    })

def get_recent_conversation(user_id):
    return list(conversation_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(5))
