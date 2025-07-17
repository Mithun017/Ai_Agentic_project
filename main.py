from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
import re

# Directly set API keys (⚠️ not recommended for production)
gemini_api_key = "AIzaSyDMjMNmOs--NydgDY4i6m9hWdNwQVKuRK4"
tavily_api_key = "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"
groq_api_key = "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"

# Validate API keys
if not gemini_api_key or not tavily_api_key or not groq_api_key:
    raise ValueError("❌ Missing one or more API keys (GEMINI_API_KEY, TAVILY_API_KEY, GROQ_API_KEY)")

# Initialize language models
gemini_llm = ChatGoogleGenerativeAI(api_key=gemini_api_key, model="gemini-2.0-flash")
groq_llm = ChatGroq(api_key=groq_api_key, model="llama-3.1-8b-instant")

# Tavily web search function
def tavily_search(query: str) -> str:
    client = TavilyClient(api_key=tavily_api_key)
    results = client.search(query=query, search_depth="advanced")
    return "\n".join([r['content'] for r in results.get('results', [])[:3]])

# HTML cleaner
def clean_output(text):
    text = re.sub(r'<sub>(.*?)</sub>', r'_\1_', text)
    text = re.sub(r'<sup>(.*?)</sup>', r'^\1^', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

# Detect emotion in user query
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

# Tone instruction based on emotion
def tone_instruction(emotion: str) -> str:
    tones = {
        "sad": "Be gentle and supportive in your tone. Offer encouragement.",
        "angry": "Stay calm and professional. Provide constructive, de-escalating language.",
        "happy": "Reflect their enthusiasm! Keep your response cheerful and positive.",
        "anxious": "Reassure the user and give confident, clear guidance.",
        "neutral": "Maintain a helpful and neutral tone."
    }
    return tones.get(emotion, tones["neutral"])

# Generate Gemini prompt
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

# Generate Groq prompt
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

# Main execution
def main():
    user_query = input("💬 Enter your query: ")

    # Emotion Detection
    emotion = detect_emotion(user_query)
    print(f"\n🧠 Detected Emotion: {emotion.capitalize()}")

    # Web Search
    print("\n🔎 Searching the web...")
    search_results = tavily_search(user_query)

    # Generate Answer with Gemini
    print("\n🤖 Creating intelligent agent response using Gemini Flash 2.0...")
    gemini_prompt = generate_gemini_prompt(search_results, user_query, emotion)
    gemini_output = gemini_llm.invoke(gemini_prompt)

    # Refine with Groq
    print("\n🎯 Polishing the response using Groq (LLaMA 3.1)...")
    groq_prompt = generate_groq_prompt(gemini_output.content, emotion)
    final_output = groq_llm.invoke(groq_prompt)

    # Final Output
    print("\n✅ FINAL OUTPUT:\n")
    print(clean_output(final_output.content))

if __name__ == "__main__":
    main()
