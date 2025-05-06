import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("groq_api_key")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# ----------------- Sidebar ----------------- #
st.sidebar.title("⚙️ Personalization")
with st.sidebar.expander("Settings", expanded=True):
    system_prompt = st.text_area("System Prompt", "You are a helpful assistant.")
    model = st.selectbox(
        "Choose a model",
        ['Llama3-8b-8192', 'Llama3-70b-8192', 'mistral-saba-24b', 'gemma2-9b-it'],
        help="Select the model to use for generating responses."
    )

    if st.button("🧹 Clear Chat History"):
        st.session_state.history = []

st.sidebar.title("📜 Chat History")
for i, entry in enumerate(st.session_state.get("history", [])):
    if st.sidebar.button(f"Q{i+1}: {entry['query']}", key=f"hist_{i}"):
        st.info(f"**Q:** {entry['query']}\n\n**A:** {entry['response']}")

# ----------------- Main ----------------- #
st.title("Chat 💭 with Groq API")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

# Multi-line chat input
user_input = st.text_area("👤 Your message:", "")

# Send message
if st.button("📤 Send") and user_input.strip():
    try:
        # Construct message history
        messages = [{"role": "system", "content": system_prompt}]
        for item in st.session_state.history:
            messages.append({"role": "user", "content": item["query"]})
            messages.append({"role": "assistant", "content": item["response"]})
        messages.append({"role": "user", "content": user_input.strip()})

        # Make API call
        response = client.chat.completions.create(
            messages=messages,
            model=model,
        ).choices[0].message.content.strip()

        # Save history
        st.session_state.history.append({"query": user_input.strip(), "response": response})

        # Display response
        st.success("🤖 Assistant:")
        st.markdown(response)

    except Exception as e:
        st.error(f"Error: {e}")

