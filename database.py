from pymongo import MongoClient
from config import MONGO_URI

try:
  client = MongoClient(MONGO_URI)
  db = client['Llama_coding_helper']
  conversation_collection = db['conversation']
  user_collection = db['user']
  print(f"MongoDB Connected")
except Exception as e:
  print(f"Error connecting to MongoDB: {e}")

