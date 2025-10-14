*🤖 AI Customer Support Bot with Memory, Gemini Fallback & Database*

*🧠 Overview*

*This project simulates an AI-powered customer support system that:*

*   *Handles FAQs and intent-based queries*
*   *Uses contextual memory for session-based chat*
*   *Falls back to Gemini API (LLM) for unseen questions*
*   *Logs low-confidence queries for human escalation*
*   *Stores full chat history in an SQLite database*

*🚀 Features*

| Feature | Description |
| --- | --- |
| 💬 Conversational Chat | Understands and replies to predefined intents & FAQs |
| 🧠 Contextual Memory | Retains session-wise conversation history |
| 🤖 LLM Fallback | Uses Gemini (via Google Generative AI) when confidence is low |
| 🧾 Escalation Logging | Unanswered queries are saved in data/escalations.json |
| 💾 Persistent Database | Stores all conversations in SQLite (chat_sessions.db) |
| 📊 Streamlit Dashboards | View chat history & session insights interactively |

*🏗 System Architecture*
plantuml
@startuml
start
:👩‍💻 User Query;
-> 🌐 FastAPI Backend;

if (🔍 Intent Match Found?) then (✅ High Confidence)
  :💬 Respond from JSON Data;
else (❌ No Match)
  :🧠 Gemini API Fallback;
  if (🔍 LLM Confidence?) then (High Confidence)
    :💬 Return LLM Response;
  else (Low Confidence)
    :📋 Log to Escalations;
    -> 🔄 Human Review Queue;
  endif
endif

:💾 Store in Database;
-> 📊 Streamlit Dashboard;
stop
@enduml


*🏗 Project Structure*

```bash

project_root/
│
├── app.py                  # FastAPI backend
├── streamlit_app.py        # Chat interface
├── history_viewer.py       # Analytics dashboard
├── database.py             # SQLAlchemy models
│
├── data/
│   ├── intents.json        # Intent patterns & responses
│   ├── faqs.json           # FAQ database
│   └── escalations.json    # Unresolved queries
│
├── models/
│   ├── chat_models.py      # Pydantic schemas
│   └── db_models.py        # Database models
│
├── utils/
│   ├── gemini_client.py    # LLM integration
│   └── similarity.py       # Intent matching
│
├── chat_sessions.db        # SQLite database
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

*⚙ Installation & Setup*

*1️⃣ Clone Repository*

```bash

git clone https://github.com/your-username/ai-customer-support-bot.git
cd ai-customer-support-bot
```

*2️⃣ Install Dependencies*

```bash
**pip install -r requirements.txt**
```

*3️⃣ Configure Environment

*Create .env file:*

```bash
# Gemini API Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Application Settings
DEBUG=True
DATABASE_URL=sqlite:///chat_sessions.db
SIMILARITY_THRESHOLD=0.7
```

*4️⃣ Initialize Database*

```bash
python database.py
```

*5️⃣ Start Backend Server*

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

*6️⃣ Launch Chat Interface*

```bash
streamlit run streamlit\_app.py
```

*7️⃣ Access Analytics Dashboard*

```bash
streamlit run history\_viewer.py
```

*🧩 API Endpoints*

| Method | Endpoint | Description | Request Body |
| --- | --- | --- | --- |
| POST | /chat | Process user message | {"session_id": "str", "message": "str"} |
| GET | /history/{session_id} | Get chat history | - |
| GET | /sessions | List all sessions | - |
| DELETE | /session/{session_id} | Clear session | - |
| GET | /health | Health check | - |



*🔹 Confidence-Based Routing*

```python
def route_query(user_input, confidence_score):
    if confidence_score >= 0.8:
        return "intent_match"
    elif confidence_score >= 0.5:
        return "llm_fallback"
    else:
        return "human_escalation"
```


*Real-time Dashboard Features*

*   *📈 Confidence score distribution*
*   *🔄 Source utilization (Intent vs LLM vs FAQ)*
*   *⏱ Average response times*
*   *🚨 Escalation trends*
*   *💬 Most common query patterns*

*📈 Performance Benchmarks*

| Metric | Value | Target |
| --- | --- | --- |
| Response Time | < 2s | < 3s |
| Intent Accuracy | 92% | > 85% |
| LLM Fallback Rate | 15% | < 20% |
| Database Query Time | < 100ms | < 200ms |

*🧑‍💻 Author*
```bash
**Harshita Baghel  | VIT Bhopal University_**
```

*🙏 Acknowledgments*

*   *Google Gemini API for powerful language model capabilities*
*   *FastAPI team for the excellent asynchronous web framework*
*   *Streamlit for making data apps accessible*
*   *SQLAlchemy for robust database ORM*
*   *SentenceTransformers for semantic similarity matching*





