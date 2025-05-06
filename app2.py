import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# -- Page Config --
st.set_page_config(page_title="ChatGPT Style Chat", page_icon="💬", layout="wide")

# Load environment
load_dotenv()
groq_api_key = os.getenv("groq_api_key")
client = Groq(api_key=groq_api_key)

# -- Theme Toggle --
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

theme_toggle = st.sidebar.toggle("🌗 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = theme_toggle

# -- CSS Styling --
dark_css = """
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp { background-color: #1E1E2F; color: #ECECF1; }
    [data-testid="stSidebar"] { background-color: #2C2C3E; }
    .stChatInput textarea {
        background-color: #2B2B3B; color: white;
        border-radius: 8px; padding: 10px;
        border: 1px solid #444;
    }
    div[data-testid="chat-message"] { margin-bottom: 1rem; }
    div[data-testid="stChatMessage"][data-label="user"] > div {
        background-color: #0E927C; color: white;
        padding: 12px 16px; border-radius: 16px;
        max-width: 65%; margin-left: auto;
    }
    div[data-testid="stChatMessage"][data-label="assistant"] > div {
        background-color: #2B2B3B; color: white;
        padding: 12px 16px; border-radius: 16px;
        max-width: 65%; margin-right: auto;
    }
    button[kind="secondary"] {
        background-color: #3A3A4D; color: white;
        border-radius: 8px; padding: 6px 12px;
    }
    button[kind="secondary"]:hover {
        background-color: #50506E;
    }
    </style>
"""

light_css = """
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp { background-color: #F7F7F8; color: #000000; }
    [data-testid="stSidebar"] { background-color: #E0E0E7; }
    .stChatInput textarea {
        background-color: #FFFFFF; color: black;
        border-radius: 8px; padding: 10px;
        border: 1px solid #CCC;
    }
    div[data-testid="chat-message"] { margin-bottom: 1rem; }
    div[data-testid="stChatMessage"][data-label="user"] > div {
        background-color: #10A37F; color: white;
        padding: 12px 16px; border-radius: 16px;
        max-width: 65%; margin-left: auto;
    }
    div[data-testid="stChatMessage"][data-label="assistant"] > div {
        background-color: #F1F1F4; color: black;
        padding: 12px 16px; border-radius: 16px;
        max-width: 65%; margin-right: auto;
    }
    button[kind="secondary"] {
        background-color: #D0D0DC; color: black;
        border-radius: 8px; padding: 6px 12px;
    }
    button[kind="secondary"]:hover {
        background-color: #BFBFCC;
    }
    </style>
"""

# Inject the CSS
st.markdown(dark_css if st.session_state.dark_mode else light_css, unsafe_allow_html=True)

# ----------------- Sidebar ----------------- #
with st.sidebar:
    st.title("⚙️ Personalization")
    system_prompt = st.text_area("System Prompt", "You are a helpful assistant.")
    model = st.selectbox(
        "Choose a model",
        ['Llama3-8b-8192', 'Llama3-70b-8192', 'mistral-saba-24b', 'gemma2-9b-it'],
    )
    if st.button("🧹 Clear Chat History"):
        st.session_state.history = []
        st.session_state.qa_history = []

    st.markdown("---")
    st.title("📜 Chat History")
    for i, entry in enumerate(st.session_state.get("qa_history", [])):
        if st.button(f"Q{i+1}: {entry['query']}", key=f"hist_{i}"):
            st.info(f"**Q:** {entry['query']}\n\n**A:** {entry['response']}")

# ----------------- Session State ----------------- #
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.qa_history = []
    st.session_state.history.append({
        "role": "assistant",
        "content": "**Welcome!** 👋\nI am your AI assistant. How can I help you today?"
    })

# ----------------- Chat Display ----------------- #
for msg in st.session_state.history:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# ----------------- Chat Input ----------------- #
if user_input := st.chat_input("Type your message..."):
    st.session_state.history.append({"role": "user", "content": user_input})
    messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.history:
        messages.append({"role": m['role'], "content": m['content']})
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=model
        ).choices[0].message.content.strip()
    except Exception as e:
        response = f"Error: {e}"

    st.session_state.history.append({"role": "assistant", "content": response})
    st.session_state.qa_history.append({"query": user_input, "response": response})
    st.rerun()
