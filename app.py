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
# CUSTOM CSS — clean light theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Page background */
    .stApp { background-color: #F0F4F8; }

    /* Main content area */
    .block-container { padding-top: 2rem; }

    /* Header banner */
    .main-header {
        background: linear-gradient(135deg, #1565C0, #1976D2);
        padding: 24px 32px; border-radius: 16px;
        margin-bottom: 24px; text-align: center;
        box-shadow: 0 4px 12px rgba(21,101,192,0.25);
    }
    .main-header h1 { color: #FFFFFF; margin: 0; font-size: 2rem; }
    .main-header p  { color: #BBDEFB; margin: 6px 0 0; font-size: 1rem; }

    /* Chat messages — user */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatar"] svg[aria-label="user"]),
    [data-testid="stChatMessage"][data-role="user"] {
        background: #1565C0 !important;
        border-radius: 14px !important;
        padding: 12px 16px !important;
    }
    [data-testid="stChatMessage"][data-role="user"] p { color: #FFFFFF !important; }

    /* Chat messages — assistant */
    [data-testid="stChatMessage"][data-role="assistant"] {
        background: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #BBDEFB !important;
        padding: 12px 16px !important;
    }
    [data-testid="stChatMessage"][data-role="assistant"] p { color: #1A1A2E !important; }

    /* Generic chat message spacing */
    [data-testid="stChatMessage"] {
        margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }

    /* Chat input box */
    [data-testid="stChatInput"] textarea {
        background: #FFFFFF;
        color: #1A1A2E;
        border: 1.5px solid #90CAF9;
        border-radius: 12px;
        font-size: 1rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1A237E;
    }
    [data-testid="stSidebar"] * { color: #E8EAF6 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: #283593;
        color: #E8EAF6 !important;
        border: 1px solid #3F51B5;
        border-radius: 8px;
        width: 100%;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #3F51B5;
    }
    [data-testid="stSidebar"] .stSelectbox label { color: #90CAF9 !important; }

    /* Sidebar info box */
    .sidebar-info {
        background: #283593; padding: 14px; border-radius: 10px;
        border: 1px solid #3F51B5; color: #BBDEFB !important;
        font-size: 0.9rem; line-height: 1.6;
    }
    .sidebar-info a { color: #82B1FF !important; }

    /* Error messages */
    [data-testid="stAlert"] { border-radius: 10px; }
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
# API KEY — from Streamlit secrets or env var
# ─────────────────────────────────────────────
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# ─────────────────────────────────────────────
# SIDEBAR — SETTINGS
# ─────────────────────────────────────────────
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
        <a href="https://aistudio.google.com">Get API Key →</a>
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
        st.error("GEMINI_API_KEY not found. Add it to Streamlit Secrets or set it as an environment variable.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-pro-latest",
        system_instruction=PERSONAS[persona]
    )

    history = []
    for msg in st.session_state.messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=history)

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
