from fastapi import APIRouter, Depends
from utils.auth_helpers import verify_token
from database import conversation_collection

router = APIRouter()

@router.post("/clear_conversation")
async def clear_conversation(current_user: str = Depends(verify_token)):
    conversation_collection.delete_many({"user_id": current_user})
    return {"message": "Conversation history cleared"}

@router.get("/conversation")
async def get_conversation(current_user: str = Depends(verify_token)):
    chat_history = list(conversation_collection.find({"user_id": current_user}).sort("timestamp", -1))
    return chat_history
