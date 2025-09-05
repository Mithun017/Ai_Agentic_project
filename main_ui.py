import streamlit as st
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.globals import set_verbose
import re
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

set_verbose(False)

gemini_api_key = "AIzaSyDpFiGLV8NlLi2_6H67tMlq_835vfttGWQ"
tavily_api_key = "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"
groq_api_key = "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"

if not gemini_api_key or not tavily_api_key or not groq_api_key:
    raise ValueError("❌ Missing one or more API keys.")

gemini_llm = ChatGoogleGenerativeAI(api_key=gemini_api_key, model="gemini-2.0-flash")
groq_llm = ChatGroq(api_key=groq_api_key, model="llama-3.1-8b-instant")

def is_valid_image_url(url: str, headers: dict) -> bool:
    """Check if the URL is likely to point to a valid image."""
    try:
        # Skip known problematic domains (e.g., YouTube thumbnails)
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'i.ytimg.com':
            print(f"Skipping YouTube thumbnail URL: {url}")
            return False
        
        # Perform a HEAD request to check accessibility
        response = requests.head(url, headers=headers, timeout=3, allow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            return 'image' in content_type
        return False
    except requests.exceptions.RequestException as e:
        print(f"Validation failed for {url}: {str(e)}")
        return False

def tavily_search(query: str) -> tuple:
    client = TavilyClient(api_key=tavily_api_key)
    results = client.search(query=query, search_depth="advanced", include_images=True)
    text_results = "\n".join([r['content'] for r in results.get('results', [])[:3]])
    
    # Handle image results
    images = results.get('images', [])
    if not images:
        image_urls = []
    elif isinstance(images[0], dict):
        image_urls = [img.get('url', '') for img in images[:3] if img.get('url')]
    else:
        image_urls = images[:3]
    
    # Filter valid image URLs
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    valid_image_urls = [url for url in image_urls if is_valid_image_url(url, headers)]
    
    print("Tavily image URLs:", image_urls)
    print("Valid image URLs:", valid_image_urls)
    
    return text_results, valid_image_urls

def clean_output(text):
    text = re.sub(r'<sub>(.*?)</sub>', r'_\1_', text)
    text = re.sub(r'<sup>(.*?)</sup>', r'^\1^', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

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

def tone_instruction(emotion: str) -> str:
    tones = {
        "sad": "Be gentle and supportive in your tone. Offer encouragement.",
        "angry": "Stay calm and professional. Provide constructive, de-escalating language.",
        "happy": "Reflect their enthusiasm! Keep your response cheerful and positive.",
        "anxious": "Reassure the user and give confident, clear guidance.",
        "neutral": "Maintain a helpful and neutral tone."
    }
    return tones.get(emotion, tones["neutral"])

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

st.set_page_config(page_title="🧠 Agentic AI Assistant", layout="wide")

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
        /* Image styling */
        .reference-image {
            max-width: 200px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
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

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="header">
            <h1>🧠 Agentic AI Assistant</h1>
            <p>Ask anything, and I'll research, think, and respond with clarity and empathy.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if "last_response" not in st.session_state:
        st.session_state.last_response = ""
    if "last_images" not in st.session_state:
        st.session_state.last_images = []

    # Display response and images at the top
    if st.session_state.last_response or st.session_state.last_images:
        st.markdown('<div class="response-card">', unsafe_allow_html=True)
        if st.session_state.last_response:
            st.markdown(st.session_state.last_response, unsafe_allow_html=True)
        if st.session_state.last_images:
            st.markdown("<h3>Reference Images</h3>", unsafe_allow_html=True)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            for img_url in st.session_state.last_images:
                try:
                    response = requests.get(img_url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'image' in content_type:
                            img = Image.open(BytesIO(response.content))
                            st.image(img, caption="Reference Image", use_container_width=False, width=200, output_format="auto")
                        else:
                            st.warning(f"URL {img_url} does not point to a valid image (Content-Type: {content_type}).")
                    else:
                        st.warning(f"Failed to load image from {img_url}. HTTP Status: {response.status_code} {'(possibly an invalid YouTube thumbnail)' if 'i.ytimg.com' in img_url else ''}")
                except requests.exceptions.Timeout:
                    st.warning(f"Request timed out for image from {img_url}.")
                except requests.exceptions.RequestException as e:
                    st.warning(f"Could not load image from {img_url}. Error: {str(e)}")
                except Exception as e:
                    st.warning(f"Failed to process image from {img_url}. Error: {str(e)}")
        else:
            st.markdown("<p>No reference images found.</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

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
            text_results, image_urls = tavily_search(user_query)

        with st.spinner("🤖 Drafting response..."):
            gemini_prompt = generate_gemini_prompt(text_results, user_query, emotion)
            gemini_output = gemini_llm.invoke(gemini_prompt)

        with st.spinner("🎯 Polishing response..."):
            groq_prompt = generate_groq_prompt(gemini_output.content, emotion)
            final_output = groq_llm.invoke(groq_prompt)

        st.session_state.last_response = clean_output(final_output.content)
        st.session_state.last_images = image_urls
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
