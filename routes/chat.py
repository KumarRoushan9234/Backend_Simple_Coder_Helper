from fastapi import APIRouter, Depends, HTTPException
from database import user_collection
from utils.auth_helpers import verify_token
from utils.chat_helpers import update_chat_history, get_recent_conversation
from models import AskModel, ModelSelection
from groq import Groq
from config import GROQ_API_KEY

router = APIRouter()
groq = Groq(api_key=GROQ_API_KEY)

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

# **Model Selection Endpoint**
@router.post("/select_model")
async def select_model(data: ModelSelection, current_user: str = Depends(verify_token)):
    try:
        if data.model not in options:
            raise HTTPException(status_code=400, detail="Invalid model selected.")

        user_collection.update_one({"_id": current_user}, {"$set": {"selected_model": data.model}})
        return {"message": f"Model '{data.model}' selected successfully", "success": True, "data": None}

    except Exception as e:
        return {"message": str(e), "success": False, "data": None}

# **Ask Question Endpoint**
@router.post("/ask")
async def ask(data: AskModel, current_user: str = Depends(verify_token)):
    try:
        user_data = user_collection.find_one({"_id": current_user})
        selected_model = user_data.get("selected_model") if user_data else None

        if not selected_model:
            raise HTTPException(status_code=400, detail="No model selected")

        chat_history = get_recent_conversation(current_user)
        messages = [{"role": "user", "content": data.user_input}]
        
        chat_completion = groq.chat.completions.create(
            messages=messages, model=selected_model, temperature=0.5
        )

        response_text = chat_completion.choices[0].message.content
        update_chat_history(data.user_input, response_text, current_user, selected_model)
        
        return {"message": "Request processed successfully", "success": True, "data": {"response": response_text}}

    except Exception as e:
        return {"message": str(e), "success": False, "data": None}
