# Codebase RAG API

FastAPI-based REST API for the Codebase RAG system.

## Endpoints

### Health Check
```
GET /health
```

### Query Code
```
POST /query
{
  "query": "How does authentication work?",
  "language": "python",
  "code_type": "function",
  "top_k": 5,
  "include_context": true
}
```

### Ingest Repository
```
POST /ingest
{
  "repo_url": "https://github.com/user/repo",
  "branch": "main",
  "extensions": [".py", ".js"]
}
```

### Explain Code
```
POST /explain
{
  "code": "def factorial(n): ...",
  "language": "python"
}
```

### Debug Help
```
POST /debug
{
  "error_message": "AttributeError: ...",
  "language": "python"
}
```

### Get Stats
```
GET /stats
```

## Running the API
```bash
# Start server
python scripts/run_api.py

# API will be at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

## Testing
```bash
# In another terminal
python scripts/test_api.py
```
