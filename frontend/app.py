"""
Codebase RAG - Streamlit Frontend
Beautiful, interactive interface for code search and Q&A.
"""

import streamlit as st
import requests
import time
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Codebase RAG - AI Code Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for beautiful styling
st.markdown(
    """
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --danger-color: #ef4444;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: #f3f4f6;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Code block styling */
    .code-block {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Source card styling */
    .source-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .source-card:hover {
        transform: translateX(5px);
    }
    
    /* Stats card */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 0.5rem 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""",
    unsafe_allow_html=True,
)

# API Configuration
API_URL = "http://localhost:8000"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "indexed_repos" not in st.session_state:
    st.session_state.indexed_repos = []


def check_api_status():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_system_stats():
    """Get system statistics."""
    try:
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}


def query_code(query, language=None):
    """Query the codebase."""
    try:
        payload = {
            "query": query,
            "language": language,
            "top_k": 5,
            "include_context": False,
        }
        response = requests.post(f"{API_URL}/query", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def ingest_repository(repo_url, branch="main"):
    """Ingest a GitHub repository."""
    try:
        payload = {
            "repo_url": repo_url,
            "branch": branch,
            "extensions": [".py", ".js", ".java", ".cpp", ".go", ".rs"],
        }
        response = requests.post(f"{API_URL}/ingest", json=payload, timeout=300)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def explain_code(code, language="python"):
    """Explain a code snippet."""
    try:
        payload = {"code": code, "language": language}
        response = requests.post(f"{API_URL}/explain", json=payload)
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to get explanation"}
    except Exception as e:
        return {"error": str(e)}


# Main Header
st.markdown(
    """
<div class="main-header">
    <h1>🤖 Codebase RAG</h1>
    <p>Your AI-Powered Code Assistant</p>
</div>
""",
    unsafe_allow_html=True,
)

# Check API status
api_status = check_api_status()

if not api_status:
    st.error(
        "⚠️ API Server is not running! Please start it with: `python scripts/run_api.py`"
    )
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Navigation")

    page = st.radio(
        "",
        ["💬 Chat", "📂 Ingest Repository", "💡 Explain Code", "📊 Statistics"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # System Stats
    stats = get_system_stats()
    st.markdown("### 📈 System Stats")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Vectors", stats.get("indexed_vectors", 0))
    with col2:
        st.metric("Dimension", stats.get("dimension", 0))

    st.markdown("---")

    # Filter options (for chat page)
    if page == "💬 Chat":
        st.markdown("### 🔍 Filters")
        language_filter = st.selectbox(
            "Language",
            ["All", "Python", "JavaScript", "Java", "C++", "Go", "Rust"],
            index=0,
        )

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("Codebase RAG uses AI to help you understand and navigate your code.")

# Main Content Area
if page == "💬 Chat":
    st.markdown("## 💬 Chat with Your Codebase")
    st.markdown("Ask questions in natural language and get AI-powered answers!")

    # Chat interface
    chat_container = st.container()

    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(
                    f"""
                <div class="user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="assistant-message">
                    <strong>🤖 Assistant:</strong><br>{message['content']}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Show sources if available
                if "sources" in message and message["sources"]:
                    with st.expander(f"📚 Sources ({len(message['sources'])})"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(
                                f"""
                            <div class="source-card">
                                <strong>{i}. {source['name']}</strong> ({source['type']})<br>
                                📁 {source['file']} <br>
                                📍 Lines {source['lines']} <br>
                                🔤 Language: {source['language']}
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

    # Query input
    st.markdown("---")
    col1, col2 = st.columns([4, 1])

    with col1:
        user_query = st.text_input(
            "Ask a question:",
            placeholder="e.g., How does user authentication work?",
            label_visibility="collapsed",
        )

    with col2:
        search_button = st.button("🚀 Search", use_container_width=True)

    if search_button and user_query:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        # Show loading
        with st.spinner("🔍 Searching codebase..."):
            lang = None if language_filter == "All" else language_filter.lower()
            result = query_code(user_query, language=lang)

        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            # Add assistant response
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result.get("sources", []),
                }
            )

        st.rerun()

elif page == "📂 Ingest Repository":
    st.markdown("## 📂 Ingest GitHub Repository")
    st.markdown("Add a new repository to your codebase search index")

    col1, col2 = st.columns([3, 1])

    with col1:
        repo_url = st.text_input(
            "GitHub Repository URL", placeholder="https://github.com/username/repo"
        )

    with col2:
        branch = st.text_input("Branch", value="main")

    if st.button("🚀 Ingest Repository", use_container_width=True):
        if repo_url:
            with st.spinner("🔄 Ingesting repository... This may take a few minutes"):
                result = ingest_repository(repo_url, branch)

            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                st.success(f"✅ Successfully ingested {result['repo_name']}!")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Files Processed", result["files_processed"])
                with col2:
                    st.metric("Chunks Created", result["chunks_created"])
                with col3:
                    st.metric("Chunks Indexed", result["chunks_indexed"])

                st.session_state.indexed_repos.append(
                    {
                        "name": result["repo_name"],
                        "url": repo_url,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
        else:
            st.warning("⚠️ Please enter a repository URL")

    # Show indexed repositories
    if st.session_state.indexed_repos:
        st.markdown("---")
        st.markdown("### 📚 Indexed Repositories")

        for repo in st.session_state.indexed_repos:
            st.markdown(
                f"""
            <div class="source-card">
                <strong>{repo['name']}</strong><br>
                🔗 {repo['url']}<br>
                ⏰ Indexed: {repo['timestamp']}
            </div>
            """,
                unsafe_allow_html=True,
            )

elif page == "💡 Explain Code":
    st.markdown("## 💡 Explain Code")
    st.markdown("Get AI-powered explanations for any code snippet")

    language = st.selectbox(
        "Programming Language", ["Python", "JavaScript", "Java", "C++", "Go", "Rust"]
    )

    code_input = st.text_area(
        "Paste your code here:",
        height=200,
        placeholder="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
    )

    if st.button("✨ Explain Code", use_container_width=True):
        if code_input:
            with st.spinner("🤔 Analyzing code..."):
                result = explain_code(code_input, language.lower())

            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                st.markdown("### 📖 Explanation")
                st.markdown(
                    f"""
                <div class="assistant-message">
                    {result.get('explanation', 'No explanation available')}
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("⚠️ Please enter some code to explain")

elif page == "📊 Statistics":
    st.markdown("## 📊 System Statistics")

    stats = get_system_stats()

    # Big stats cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
        <div class="stat-card">
            <div>Indexed Vectors</div>
            <div class="stat-value">{stats.get('indexed_vectors', 0):,}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="stat-card">
            <div>Embedding Dimension</div>
            <div class="stat-value">{stats.get('dimension', 0)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="stat-card">
            <div>Status</div>
            <div class="stat-value">✅</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Chat history stats
    st.markdown("### 💬 Chat Statistics")

    total_messages = len(st.session_state.chat_history)
    user_messages = len(
        [m for m in st.session_state.chat_history if m["role"] == "user"]
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Messages", total_messages)
    with col2:
        st.metric("Your Questions", user_messages)

    # Repository stats
    st.markdown("### 📚 Repository Statistics")
    st.metric("Indexed Repositories", len(st.session_state.indexed_repos))

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666; padding: 1rem;">
    Made with ❤️ using Streamlit | Powered by AI<br>
    <small>Codebase RAG v1.0.0</small>
</div>
""",
    unsafe_allow_html=True,
)
