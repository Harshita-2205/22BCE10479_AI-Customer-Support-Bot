import streamlit as st
import requests
import uuid

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="AI Customer Support Bot", page_icon="🤖", layout="centered")

FASTAPI_URL = "http://127.0.0.1:8000/chat"  # backend endpoint

# -----------------------------
# SESSION STATE
# -----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("💬 AI Customer Support Assistant")


# -----------------------------
# CHAT INPUT
# -----------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    # Append user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Send to FastAPI backend
    payload = {"session_id": st.session_state.session_id, "query": user_input}

    try:
        response = requests.post(FASTAPI_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            bot_msg = f"{data['response']}`"
        else:
            bot_msg = "⚠️ Error: Could not get response from backend."
    except Exception as e:
        bot_msg = f"🚨 Connection error: {e}"

    # Append bot response
    st.session_state.chat_history.append({"role": "bot", "content": bot_msg})

# -----------------------------
# DISPLAY CHAT
# -----------------------------
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"👤 **You:** {msg['content']}")
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("Built by Harshita 💙")
