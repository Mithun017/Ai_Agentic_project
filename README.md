# 🤖 AI_Agentic-An AI assistant that thinks, researches, and responds with clarity.

An AI-powered multi-agent system that searches the web, generates detailed answers using Gemini, and refines them using Groq’s LLaMA models. The system is designed to run locally using Docker and requires no manual setup once the image is built.

🌐 **Deployed App:** [https://ai-agentic-chat.streamlit.app/](https://ai-agentic-chat.streamlit.app/)

---

## 🚀 Features

* 🔍 Web Search using Tavily API
* 🧠 Answer Generation via Google Gemini (Gemini 2.0 Flash)
* ✨ Answer Refinement via Groq LLaMA (llama-3.1-8b-instant)
* 🐳 Dockerized for easy deployment
* 🔐 Optional: Secure `.env` configuration
* 📃 Streamlit UI with ChatGPT-like experience

---

## 📁 Project Structure

```
ai_agentic_project/
│
├── main.py                # Main logic for multi-agent flow
├── main_ui.py             # Streamlit UI app (ChatGPT-like interface)
├── requirements.txt       # All dependencies
├── Dockerfile             # Docker setup
├── .env (optional)        # Contains API keys (not pushed to GitHub)
├── README.md              # This file
├── main.ipynb             # Jupyter notebook (optional usage)
├── Test_prompt.txt        # Sample prompts for testing
└── .gitignore             # Ignore sensitive or system files
```

---

## 🧠 Agents

### 🔹 Gemini Agent

* Uses `langchain_google_genai` and `gemini-2.0-flash`
* Generates detailed answers from Tavily search results

### 🔹 Groq Agent

* Uses `langchain_groq` with `llama-3.1-8b-instant`
* Refines Gemini’s output into final polished response

---

## 🛠️ Requirements

* Python 3.8+
* Docker installed

---

## 🔑 Environment Variables

You can either:

* Pass environment variables with `--env` flags (safe method), **or**
* Hardcode them in the script (less secure, but portable via Docker image)

### .env format (optional):

```env
GROQ_API_KEY=your-groq-key
TAVILY_API_KEY=your-tavily-key
GEMINI_API_KEY=your-gemini-key
```

---

## 🐳 Docker Setup

### 🔨 Step 1: Build the Docker Image

```bash
docker build -t my-main-app .
docker tag my-main-app mithun1701/my-main-app:latest
```

### ♻️ Step 2: Run the Container (with environment variables)

```bash
docker run -it --rm \
  -e GROQ_API_KEY=your-groq-key \
  -e TAVILY_API_KEY=your-tavily-key \
  -e GEMINI_API_KEY=your-gemini-key \
  mithun1701/my-main-app:latest
```

### ✅ OR: Run Without .env (if hardcoded inside image)

```bash
docker pull mithun1701/my-main-app:latest

docker run -it mithun1701/my-main-app:latest
```

---

## 🔄 Updating the Docker Image (after code changes)

```bash
docker build -t mithun1701/my-main-app .
docker push mithun1701/my-main-app:latest
```

---

## 📅 Running the Streamlit UI

### ✨ Launch the chat UI with:

```bash
streamlit run main_ui.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser to interact with the AI Assistant.

🌐 **Live Version:** [https://ai-agentic-chat.streamlit.app/](https://ai-agentic-chat.streamlit.app/)

---

## 🔪 Sample Output (CLI)

```bash
💬 Enter your query:
> What is LangChain?

🔍 Searching the web...

🧠 Generating detailed answer with Gemini...

✨ Refining answer with Groq...

✅ FINAL OUTPUT:
Here is a polished and refined version of your response:
"LangChain is an open-source framework for building applications with LLMs..."
```

---

## 👨‍💻 Author

**Mithun** — [GitHub](https://github.com/mithun1701)
🌐 Powered by Gemini + Groq + Tavily + LangChain + Streamlit

---

## ⚠️ Disclaimer

This project is intended for educational/research purposes. Do **not** hardcode sensitive API keys in production Docker images or commit `.env` files.

---

## 📄 License

MIT License — Feel free to use, modify, and share 🚀
