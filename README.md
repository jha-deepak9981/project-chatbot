# 🤖 AI Chatbot — Powered by Gemini

A conversational AI chatbot with multiple personas, built with Streamlit and Google Gemini.

## ✨ Features
- 5 Chat personas: Friendly, Socratic Tutor, Motivational Coach, Technical Expert, Debate Partner
- Streaming responses for real-time feel
- Full conversation history maintained
- Quick starter buttons for instant prompts
- Clean dark-themed UI

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI Model:** Google Gemini 1.5 Flash
- **Language:** Python 3.10+

## 🚀 Deploy to Streamlit Cloud (Free!)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "AI Chatbot - Gemini powered"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-chatbot.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New App**
4. Select your repo → `app.py` → Deploy!
5. Done — your app is live in ~2 minutes 🎉

### Step 3: Add API Key (Optional — Secure Method)
In Streamlit Cloud → Settings → Secrets:
```toml
GEMINI_API_KEY = "your_api_key_here"
```

## 🔑 Get Free Gemini API Key
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key** → Create API Key
3. Copy and paste it in the app sidebar

## 📦 Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```
