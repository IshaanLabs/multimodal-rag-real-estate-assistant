# AI Real Estate Assistant (RAG) | Streamlit + FastAPI Chatbot with Image Retrieval & Lead Intelligence

A Retrieval-Augmented Generation (RAG) chatbot that answers property queries using PDFs, returns floorplan images, and detects buyer intent for smarter real estate engagement.

## 📋 Project Description

A production-style AI assistant built using Streamlit and FastAPI that enables intelligent conversations over real estate documents. The system leverages a RAG pipeline to extract insights from PDF-based villa floorplans (Al Badia Villas, Dubai), returning precise answers with citations and relevant images.

Beyond Q&A, the system identifies lead intent signals (e.g., buying interest, budget queries, visit requests) to assist sales workflows and next-best actions. Designed for scalability and extensibility, this project demonstrates real-world applications of LLMs in property discovery, customer engagement, and AI-driven sales enablement.

## 🔍 What It Does / How It Works

- **Document Ingestion & Indexing** Parses villa floorplan PDFs, performs intelligent text chunking, generates embeddings, and stores them in a vector database (FAISS). Floorplan images (WebP) are mapped to their corresponding semantic chunks for multimodal retrieval.
- **Query Processing (RAG Pipeline)** On each user query, the system generates embeddings, retrieves the most relevant context from the vector store, aligns associated floorplan images, and produces a grounded response using an OpenAI LLM with built-in guardrails.
- **Multimodal Response Generation** Returns context-aware answers enriched with source citations and relevant floorplan visuals, improving interpretability and user trust.
- **Lead Intent Detection & Insights** Analyzes user queries to identify buyer signals such as budget, timeline, and preferences, enabling intelligent lead qualification and suggesting next-best actions.
- **Interactive Streamlit Experience** Provides a clean chat interface with conversational flow, image rendering, citations, and actionable insights, along with quick follow-up prompts to guide user interaction.

## 🏗️ Technical Architecture

```
PDF ──→ Chunking ──→ OpenAI Embeddings ──→ FAISS Index ──→ Image Mapping
                                                │
User Query ──→ Embed ──→ FAISS Retrieval ──→ OpenAI Chat Completion ──→ Response
                                                │
                                    Lead Signal Detection ──→ Scoring & Actions
                                                │
                                        Streamlit Frontend
                              (Chat Bubbles / Images / Citations / Lead Insights)
```

- **Data ingestion:** PDF → chunking → OpenAI embeddings → FAISS index → image mapping.
- **RAG serving:** FastAPI `/chat` uses FAISS retrieval + OpenAI chat completion with context.
- **Lead analysis:** Regex-based signal detection, scoring, recommended action, follow-up prompt.
- **Frontend:** Streamlit app (with `streamlit-chat`) calling the FastAPI backend.

## ✨ Key Features

- 🤖 **RAG-Powered Answers with Citations**  
  Generates accurate, context-aware responses grounded in floorplan PDFs using Retrieval-Augmented Generation (RAG), with source-backed citations for transparency.

- 🖼️ **Intelligent Floorplan Image Retrieval**  
  Dynamically selects and displays relevant floorplan images based on villa type, layout, and document context.

- 🎯 **Lead Intent Detection & Actionable Insights**  
  Identifies key buyer signals (budget, timeline, preferences) and recommends next-best actions to support sales workflows.

- ⚡ **Guided Conversation with Smart Follow-Ups**  
  Provides contextual prompt shortcuts to keep users engaged and streamline property discovery.

- 🎛️ **Interactive UI Controls**  
  Toggle visibility for images, citations, and lead insights to customize the user experience.

## 📁 Project Structure

```
march2026/
├── main.py               # FastAPI app entrypoint
├── data_ingestion.py     # PDF loading, chunking, embeddings, FAISS index, image map
├── rag_functions.py      # Retrieval, response generation, citations, image selection
├── lead_functions.py     # Lead signal detection, scoring, follow-up
├── streamlit_app.py      # Streamlit UI with chat bubbles, images, citations, lead insights
├── requirements.txt      # Python dependencies
├── .env                  # Configuration (API keys)
├── .streamlit/
│   └── secrets.toml      # Streamlit secrets (API_URL, etc.)
└── data/                 # PDF and WebP floorplan assets
```

## ⚙️ Installation

1. Clone the repo and navigate to the project:
   ```bash
   git clone <repo-url>
   cd march2026
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   pip install -r requirements.txt
   pip install streamlit streamlit-chat
   ```

3. Set up environment:
   - Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`.
   - Set `API_URL` in `.streamlit/secrets.toml`:
     ```toml
     API_URL = "http://localhost:8000"
     ```

## ▶️ Usage

1. **Start the backend:**
   ```bash
   python main.py
   ```
   FastAPI runs on `http://localhost:8000`. Ensure static files are mounted to serve images (e.g., `/static/WebP/...`).

2. **Start the UI:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. Open the Streamlit URL, enter a session ID, toggle images/citations/lead insights, and chat.

## 🧪 Example Queries

- "Show me the 4-bedroom villa floorplan."
- "What are the villa types available?"
- "I have a budget of 5M AED and need 3 bedrooms."

## 🛠️ Technologies Used

| Name | Description | Link |
|------|-------------|------|
| FastAPI | API server and `/chat` endpoint | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| Streamlit | Frontend UI framework | [streamlit.io](https://streamlit.io/) |
| streamlit-chat | Chat bubble component for Streamlit | [GitHub](https://github.com/AI-Yash/st-chat) |
| OpenAI API | Embeddings (`text-embedding-ada-002`) and chat | [platform.openai.com](https://platform.openai.com/) |
| FAISS | Vector similarity search index | [GitHub](https://github.com/facebookresearch/faiss) |
| numpy | Array operations for embeddings | [numpy.org](https://numpy.org/) |
| requests | HTTP calls to OpenAI and backend | [PyPI](https://pypi.org/project/requests/) |

## 🤝 Contributing

- Fork the repo, create a feature branch, and submit a PR.
- Add tests where relevant (e.g., chunking, retrieval, lead signals).
- Keep configuration out of source control (use `.env` / `.streamlit/secrets.toml`).

## 📄 License

This project is licensed under the [MIT License](LICENSE).
