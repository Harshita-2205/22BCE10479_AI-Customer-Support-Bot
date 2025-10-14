from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, random, uuid, os
from difflib import SequenceMatcher
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy.orm import Session
from database import ChatHistory, SessionLocal  # <-- import DB

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="AI Customer Support Bot with Gemini + SQLite DB")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Load Intents and FAQs
# -----------------------------
with open("data/intents.json", "r", encoding="utf-8") as f:
    intents = json.load(f)["intents"]

with open("data/faqs.json", "r", encoding="utf-8") as f:
    faqs = json.load(f)

# -----------------------------
# Helper Functions
# -----------------------------
def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_intent_response(user_input):
    best_match = (None, 0.0)
    for intent in intents:
        for pattern in intent["patterns"]:
            score = similarity(user_input, pattern)
            if score > best_match[1]:
                best_match = (intent, score)
    if best_match[0] and best_match[1] > 0.7:
        return random.choice(best_match[0]["responses"]), best_match[1]
    return None, best_match[1]

def find_faq_response(user_input):
    best_match = (None, 0.0)
    for faq in faqs:
        score = similarity(user_input, faq["question"])
        if score > best_match[1]:
            best_match = (faq, score)
    if best_match[0] and best_match[1] > 0.7:
        return best_match[0]["answer"], best_match[1]
    return None, best_match[1]

def log_message(db: Session, session_id, role, message, confidence=None, source=None):
    """Store each chat message permanently."""
    chat = ChatHistory(
        session_id=session_id,
        role=role,
        message=message,
        confidence=str(confidence) if confidence else None,
        source=source,
    )
    db.add(chat)
    db.commit()

def ask_gemini_fallback(user_input):
    """Use Gemini API to generate a helpful response."""
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(
            f"You are an AI customer support assistant. Please answer this user query: {user_input}"
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

# -----------------------------
# Request/Response Models
# -----------------------------
class ChatRequest(BaseModel):
    session_id: str | None = None
    query: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    confidence: float
    source: str

# -----------------------------
# Chat Endpoint
# -----------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    user_input = request.query.strip()
    session_id = request.session_id or str(uuid.uuid4())

    if not user_input:
        return {
            "response": "Please enter a message.",
            "session_id": session_id,
            "confidence": 0.0,
            "source": "none",
        }

    # Log user message
    log_message(db, session_id, "user", user_input)

    # Step 1: Intents
    intent_response, intent_score = find_intent_response(user_input)
    if intent_response:
        log_message(db, session_id, "bot", intent_response, intent_score, "intent")
        return {
            "response": intent_response,
            "session_id": session_id,
            "confidence": round(intent_score, 2),
            "source": "intent",
        }

    # Step 2: FAQs
    faq_response, faq_score = find_faq_response(user_input)
    if faq_response:
        log_message(db, session_id, "bot", faq_response, faq_score, "faq")
        return {
            "response": faq_response,
            "session_id": session_id,
            "confidence": round(faq_score, 2),
            "source": "faq",
        }

    # Step 3: LLM (Gemini) Fallback
    combined_conf = max(intent_score, faq_score)
    if combined_conf < 0.7:
        llm_answer = ask_gemini_fallback(user_input)
        if llm_answer:
            log_message(db, session_id, "bot", llm_answer, combined_conf, "gemini")
            return {
                "response": llm_answer,
                "session_id": session_id,
                "confidence": round(combined_conf, 2),
                "source": "gemini",
            }

    # Step 4: Escalation
    fallback = "I'm not confident about this one. Let me connect you with a human support agent."
    log_message(db, session_id, "bot", fallback, combined_conf, "escalation")
    return {
        "response": fallback,
        "session_id": session_id,
        "confidence": round(combined_conf, 2),
        "source": "escalation",
    }

# -----------------------------
# Get Chat History (from DB)
# -----------------------------
@app.get("/history/{session_id}")
async def get_history(session_id: str, db: Session = Depends(get_db)):
    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.timestamp)
        .all()
    )
    history = [
        {
            "role": c.role,
            "message": c.message,
            "source": c.source,
            "confidence": c.confidence,
            "timestamp": c.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for c in chats
    ]
    return {"session_id": session_id, "history": history}

@app.get("/")
async def root():
    return {"message": "AI Customer Support Bot with Gemini + SQLite DB is running!"}
