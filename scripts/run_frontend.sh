#!/bin/bash
# Launch script for Streamlit frontend

echo "🚀 Starting Codebase RAG Frontend..."
echo "Frontend will be available at: http://localhost:8501"
echo ""

cd "$(dirname "$0")/.."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
