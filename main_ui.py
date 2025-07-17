import streamlit as st
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.globals import set_verbose  # Import to manage verbosity
import re

# Set verbosity globally (optional: set to False to suppress detailed logs)
set_verbose(False)

# API Keys (⚠️ Do not expose in production)
gemini_api_key = "AIzaSyDMjMNmOs--NydgDY4i6m9hWdNwQVKuRK4"
tavily_api_key = "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"
groq_api_key = "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"

# Validate keys
if not gemini_api_key or not tavily_api_key or not groq_api_key:
    raise ValueError("❌ Missing one or more API keys.")

# Initialize models
gemini_llm = ChatGoogleGenerativeAI(api_key=gemini_api_key, model="gemini-2.0-flash")
groq_llm = ChatGroq(api_key=groq_api_key, model="llama-3.1-8b-instant")

# Tavily search
def tavily_search(query: str) -> str:
    client = TavilyClient(api_key=tavily_api_key)
    results = client.search(query=query, search_depth="advanced")
    return "\n".join([r['content'] for r in results.get('results', [])[:3]])

# Clean HTML
def clean_output(text):
    text = re.sub(r'<sub>(.*?)</sub>', r'_\1_', text)
    text = re.sub(r'<sup>(.*?)</sup>', r'^\1^', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

# Emotion detection
def detect_emotion(text: str) -> str:
    emotion_map = {
        "sad": ["sad", "depressed", "unhappy", "frustrated", "disappointed"],
        "angry": ["angry", "mad", "furious", "irritated"],
        "happy": ["happy", "excited", "joyful", "glad", "pleased"],
        "anxious": ["worried", "anxious", "nervous", "concerned", "afraid"],
        "neutral": []
    }
    text_lower = text.lower()
    for emotion, keywords in emotion_map.items():
        if any(word in text_lower for word in keywords):
            return emotion
    return "neutral"

# Tone instructions
def tone_instruction(emotion: str) -> str:
    tones = {
        "sad": "Be gentle and supportive in your tone. Offer encouragement.",
        "angry": "Stay calm and professional. Provide constructive, de-escalating language.",
        "happy": "Reflect their enthusiasm! Keep your response cheerful and positive.",
        "anxious": "Reassure the user and give confident, clear guidance.",
        "neutral": "Maintain a helpful and neutral tone."
    }
    return tones.get(emotion, tones["neutral"])

# Gemini prompt
def generate_gemini_prompt(search_results: str, user_query: str, emotion: str):
    tone = tone_instruction(emotion)
    return PromptTemplate.from_template(f"""
You are a highly intelligent assistant helping a user solve a complex question.

Steps:
1. Analyze the following web search results.
2. Extract key facts, insights, and evidence.
3. Respond clearly, structured, and tailored to the user's emotional tone.

Tone Guide: {tone}

Structure your output like this:
🔍 Insight Summary  
📌 Key Points  
🧠 Agent’s Thought Process  
✅ Final Answer (Empathetic or appropriate to emotional context)

Search Results:
{{search_results}}

User Query:
{{user_query}}
""").format(search_results=search_results, user_query=user_query)

# Groq prompt
def generate_groq_prompt(draft: str, emotion: str):
    tone = tone_instruction(emotion)
    return PromptTemplate.from_template(f"""
You are a language expert with emotional intelligence and excellent writing skills.

Improve the following draft by:
- Enhancing structure and flow.
- Polishing grammar and clarity.
- Making the answer more engaging.
- Adapting tone to the user's emotion: {tone}

Draft Response:
{{draft}}
""").format(draft=draft)

# Streamlit App UI
st.set_page_config(page_title="🧠 Agentic AI Assistant", layout="wide")

# Custom CSS for dark theme and ChatGPT-like UI
st.markdown(
    """
    <style>
        /* General styling */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #1a1a1a;
            color: #d1d5db;
        }
        .main-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 28px;
            color: #e0e0e0;
        }
        .header p {
            font-size: 14px;
            color: #a0a0a0;
        }
        /* Bottom input bar */
        .bottom-input {
            position: fixed;
            bottom: 20px;
            left: 50px;
            right: 50px;
            background-color: #2a2a2a;
            padding: 10px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            display: flex;
            align-items: center;
            border: 1px solid #3a3a3a;
        }
        .stTextInput input {
            border: none;
            background-color: #333;
            color: #d1d5db;
            font-size: 16px;
            padding: 12px;
            width: 100%;
            outline: none;
            border-radius: 8px;
        }
        .send-button {
            background-color: #10a37f;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s ease;
            margin-left: 10px;
        }
        .send-button:hover {
            background-color: #0e8c6b;
        }
        /* Response card */
        .response-card {
            background-color: #2a2a2a;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            border-left: 4px solid #10a37f;
            font-size: 16px;
            line-height: 1.6;
            white-space: pre-wrap;
            animation: fadeIn 0.3s ease-in;
            color: #d1d5db;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        /* Spinner */
        .stSpinner {
            color: #10a37f;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Main container
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown(
        """
        <div class="header">
            <h1>🧠 Agentic AI Assistant</h1>
            <p>Ask anything, and I'll research, think, and respond with clarity and empathy.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Initialize session state
    if "last_response" not in st.session_state:
        st.session_state.last_response = ""

    # Display response at the top
    if st.session_state.last_response:
        st.markdown(f'<div class="response-card">{st.session_state.last_response}</div>', unsafe_allow_html=True)

    # Bottom input bar
    with st.form(key="chat_form", clear_on_submit=True):
        st.markdown('<div class="bottom-input">', unsafe_allow_html=True)
        col1, col2 = st.columns([10, 1])
        with col1:
            user_query = st.text_input("Your message", label_visibility="collapsed", placeholder="Type your question...")
        with col2:
            submitted = st.form_submit_button("➤", help="Send your query")
        st.markdown('</div>', unsafe_allow_html=True)

    # Process user input
    if submitted and user_query:
        with st.spinner("🧠 Detecting emotion..."):
            emotion = detect_emotion(user_query)

        with st.spinner("🔎 Searching the web..."):
            search_results = tavily_search(user_query)

        with st.spinner("🤖 Drafting response..."):
            gemini_prompt = generate_gemini_prompt(search_results, user_query, emotion)
            gemini_output = gemini_llm.invoke(gemini_prompt)

        with st.spinner("🎯 Polishing response..."):
            groq_prompt = generate_groq_prompt(gemini_output.content, emotion)
            final_output = groq_llm.invoke(groq_prompt)

        st.session_state.last_response = clean_output(final_output.content)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)