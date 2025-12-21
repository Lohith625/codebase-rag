# Codebase RAG - Chat with Your Code

An intelligent assistant that allows developers to chat with their codebase using RAG (Retrieval Augmented Generation).

## Features

- 🔍 Semantic code search
- 💬 Natural language queries
- 🎯 Accurate code retrieval
- 📊 AST-based parsing
- 🚀 Fast vector search
- 🔄 Auto-updates on commits

## Tech Stack

- **Backend**: FastAPI, LangChain, LlamaIndex
- **Vector DB**: FAISS / Pinecone
- **LLM**: Google Gemini Flash
- **Code Parsing**: Tree-sitter
- **Frontend**: Streamlit / React

## Setup

1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your API keys
6. Run: `streamlit run frontend/streamlit_app.py`

## Project Structure
```
codebase-rag/
├── backend/
│   ├── ingestion/      # Repository loading
│   ├── parsing/        # Code parsing & chunking
│   ├── retrieval/      # Vector search & retrieval
│   ├── llm/           # LLM integration
│   └── api/           # FastAPI endpoints
├── frontend/          # UI (Streamlit/React)
├── data/             # Data storage
├── tests/            # Unit tests
└── config/           # Configuration
```

## Usage
```python
# Coming soon...
```

## License

MIT
