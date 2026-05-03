import os
import streamlit as st
import google.generativeai as genai

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Chatbot | Gemini",
    page_icon="🤖",
    layout="centered"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a1628; }
    .main-header {
        background: linear-gradient(135deg, #065A82, #1C7293);
        padding: 24px 32px; border-radius: 16px;
        margin-bottom: 24px; text-align: center;
    }
    .main-header h1 { color: #00B4D8; margin: 0; font-size: 2rem; }
    .main-header p  { color: #90E0EF; margin: 4px 0 0; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    .stTextInput > div > div > input {
        background: #0D2137; color: white; border: 1px solid #1C7293; border-radius: 10px;
    }
    .sidebar-info {
        background: #0D2137; padding: 16px; border-radius: 12px;
        border: 1px solid #1C7293; color: #90E0EF;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Chatbot</h1>
    <p>Powered by Google Gemini • Ask me anything!</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR — API KEY + SETTINGS
# ─────────────────────────────────────────────
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    st.markdown("### 🎛️ Chatbot Persona")
    persona = st.selectbox("Choose mode:", [
        "Friendly Assistant",
        "Socratic Tutor (questions only)",
        "Motivational Coach",
        "Technical Expert",
        "Debate Partner",
    ])

    st.markdown("---")
    st.markdown("### 💡 Quick Starters")
    starters = [
        "Explain quantum computing simply",
        "What career should I pick?",
        "How does AI actually learn?",
        "Give me a fun fact about space",
    ]
    for s in starters:
        if st.button(s, use_container_width=True):
            st.session_state.pending_input = s

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div class="sidebar-info">
        <b>About</b><br>
        Model: gemini-pro-latest<br>
        Context: Full history<br>
        <a href="https://aistudio.google.com" style="color:#00B4D8">Get API Key →</a>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""

# ─────────────────────────────────────────────
# PERSONA SYSTEM PROMPTS
# ─────────────────────────────────────────────
PERSONAS = {
    "Friendly Assistant":              "You are a friendly, helpful AI assistant. Be warm, clear, and concise.",
    "Socratic Tutor (questions only)": "You are a Socratic tutor. Instead of giving answers, guide the user with thoughtful questions to help them discover answers themselves.",
    "Motivational Coach":              "You are an enthusiastic motivational coach. Be energetic, positive, and help the user believe in themselves.",
    "Technical Expert":                "You are a highly technical expert. Give precise, detailed, expert-level answers with examples and code when relevant.",
    "Debate Partner":                  "You are a debate partner. For any topic presented, argue the opposing viewpoint thoughtfully and rigorously.",
}

# ─────────────────────────────────────────────
# DISPLAY CHAT HISTORY
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
pending = st.session_state.pop("pending_input", "") if "pending_input" in st.session_state else ""
user_input = st.chat_input("Type your message here...") or pending

if user_input:
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar to start chatting.")
        st.stop()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build Gemini message history
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-pro-latest",
        system_instruction=PERSONAS[persona]
    )

    history = []
    for msg in st.session_state.messages[:-1]:  # exclude last (current user msg)
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=history)

    # Stream response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_placeholder = st.empty()
            full_response = ""
            try:
                response = chat.send_message(user_input, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {e}"
                response_placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
