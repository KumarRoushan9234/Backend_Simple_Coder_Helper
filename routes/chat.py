from fastapi import APIRouter, Depends, HTTPException, Request
from database import user_collection, conversation_collection
from utils.auth_helpers import verify_token, decode_jwt_token
from utils.chat_helpers import update_chat_history, get_recent_conversation,get_CurrentUser
from models import AskModel, ModelSelection
from groq import Groq
from config import GROQ_API_KEY
from bson import ObjectId

router = APIRouter()
groq = Groq(api_key=GROQ_API_KEY)

# List of available models for selection
options = [
    "Select a model", 
    "mixtral-8x7b-32768", 
    "llama-3.3-70b-specdec", 
    "llama-3.3-70b-versatile", 
    "llama3-8b-8192", 
    "llama-guard-3-8b", 
    "llama3-70b-8192", 
    "llama-3.2-1b-preview", 
    "whisper-large-v3-turbo", 
    "llama-3.2-3b-preview", 
    "llama-guard-3-8b", 
    "gemma2-9b-it", 
    "distil-whisper-large-v3-en"
]

# ----------------- Model Selection Endpoint -----------------
@router.post("/select_model") # status - ok
async def select_model(data: ModelSelection, request: Request):
    user = get_CurrentUser(request)
    
    if not user:
        raise HTTPException(status_code=401, detail="User authentication failed")

    # Convert string `_id` to ObjectId for MongoDB queries
    user_id = ObjectId(user["_id"])

    user_doc = user_collection.find_one({"_id": user_id}, {"password": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found in the database")

    print("User authenticated", {
        "id": str(user_doc["_id"]),
        "name": user_doc.get("name", "Unknown"),
        "email": user_doc["email"],
        "username": user_doc["username"],
        "selected_model": user_doc.get("selected_model", "None"),
    })

    if data.model not in options:
        raise HTTPException(status_code=400, detail="Invalid model selected")

    # Update selected model in MongoDB
    user_collection.update_one({"_id": user_id}, {"$set": {"selected_model": data.model}})
    
    return {
        "message": f"Model '{data.model}' selected successfully",
        "success": True,
        "data": None
    }

# ----------------- Ask Question Endpoint -----------------
@router.post("/ask") # status - ok
async def ask(data: AskModel,request:Request):
    user = get_CurrentUser(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    selected_model = user.get("selected_model") if user else None
    if not selected_model:
        print("No Model Found!")
        raise HTTPException(status_code=400, detail="No model found")
    
    messages = [{"role": "user", "content": data.user_input}]
    
    chat_completion = groq.chat.completions.create(
        messages=messages, model=selected_model, temperature=0.6
    )
    response_text = chat_completion.choices[0].message.content
    
    print("Response : ",response_text)
    update_chat_history(data.user_input, response_text, str(user["_id"]), selected_model)
    
    return {
        "user_id":user["_id"],
        "message": "Request processed successfully", 
        "success": True, 
        "data": {"response": response_text, "model": selected_model}
    }

# ----------------- Clear Conversation Endpoint -----------------
@router.post("/clear_conversation") # status - ok
async def clear_conversation(request: Request):
    user = get_CurrentUser(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    conversation_collection.delete_one({"user_id": str(user["_id"])})

    return {"message": "Conversation history cleared", "success": True}

# ----------------- Get Conversation Endpoint -----------------
@router.get("/get_conversation") 
async def get_conversation(request: Request):

    user = get_CurrentUser(request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    doc = conversation_collection.find_one({"user_id":str(user["_id"])})
    conversation = doc.get("conversation", []) if doc else []
    
    conversation = conversation[-10:]
    return {"message": "Conversation fetched successfully", "success": True, "data": conversation}
