import os
import sqlite3
from fastapi import FastAPI
import google.generativeai as genai

app = FastAPI()

# 1. SETUP RENDER PERSISTENT STORAGE FOR SQLITE
# Render provides a /data directory for persistent disks so data never vanishes
DB_DIR = "/data"
if not os.path.exists(DB_DIR):
    # If testing locally on your laptop, it will just use your current folder
    DB_DIR = "."

DB_PATH = os.path.join(DB_DIR, "dr_tamilan.db")

# 2. INITIALIZE DATABASE
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 3. CONFIGURE GOOGLE AI STUDIO KEY
# Render lets us hide our API key safely in "Environment Variables"
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

@app.get("/")
def home():
    return {"status": "Soul Premium Backend Engine is running smoothly. Ready for action!"}

@app.post("/chat")
async def chat_endpoint(message: str):
    try:
        # Call the Gemini Engine
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(message)
        bot_reply = response.text
        
        # Save the conversation history safely to SQLite disk
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chat_logs (user_message, bot_response) VALUES (?, ?)', (message, bot_reply))
        conn.commit()
        conn.close()
        
        return {"response": bot_reply}
        
    except Exception as e:
        return {"error": str(e)}