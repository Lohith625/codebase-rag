"""
Codebase RAG - Modern Streamlit Frontend
Beautiful, interactive interface for code search and Q&A.
"""

import streamlit as st
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Codebase RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI-Powered Code Search with RAG"
    }
)

# Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    /* Content Area */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: fadeIn 0.6s ease-in;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        animation: slideDown 0.8s ease-out;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin-bottom: 0;
    }
    
    /* Card Styles */
    .custom-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Message Bubbles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.4s ease-out;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2d3748;
        padding: 1.2rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        animation: slideInLeft 0.4s ease-out;
    }
    
    /* Source Cards */
    .source-card {
        background: white;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .source-card:hover {
        background: #f7fafc;
        border-left-color: #764ba2;
        transform: translateX(10px);
    }
    
    /* Stats Display */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: scale(1.05);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Loading Spinner */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f7fafc;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Code blocks */
    code {
        background: #2d3748;
        color: #68d391;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000"

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'indexed_repos' not in st.session_state:
    st.session_state.indexed_repos = []
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

# Helper Functions
def check_api_status():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def get_system_stats():
    """Get system statistics."""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🤖 Codebase RAG</div>
    <div class="hero-subtitle">Ask questions about your code in natural language</div>
</div>
""", unsafe_allow_html=True)

# Check API Status
api_online, health_data = check_api_status()

if not api_online:
    st.error("⚠️ **API Server Offline** - Please start: `python scripts/run_api.py`")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Navigation")
    page = st.radio(
        "",
        ["💬 Chat", "📂 Ingest Repository", "💡 Explain Code", "📊 Dashboard"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Stats
    stats = get_system_stats()
    st.markdown("### 📈 Quick Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Vectors", f"{stats.get('indexed_vectors', 0):,}")
    with col2:
        st.metric("Queries", st.session_state.total_queries)
    
    st.markdown("---")
    
    # Filters (for chat page)
    if page == "💬 Chat":
        st.markdown("### 🔍 Filters")
        language = st.selectbox(
            "Language",
            ["All", "Python", "JavaScript", "Java", "C++", "Go", "Rust"],
            index=0
        )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("AI-powered semantic search for your codebase using RAG")

# Main Content
if page == "💬 Chat":
    st.markdown("## 💬 Chat with Your Codebase")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong><br>{msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 Assistant:</strong><br>{msg['content']}
                </div>
                """, unsafe_allow_html=True)
                
                if 'sources' in msg and msg['sources']:
                    with st.expander(f"📚 {len(msg['sources'])} Sources", expanded=False):
                        for i, src in enumerate(msg['sources'], 1):
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>{i}. {src['name']}</strong> ({src['type']})<br>
                                📁 <code>{src['file']}</code> | 
                                📍 Lines {src['lines']} | 
                                🎯 Relevance: {src['relevance']:.2f}
                            </div>
                            """, unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_query = st.text_input(
            "Ask a question:",
            placeholder="e.g., How does authentication work?",
            label_visibility="collapsed",
            key="query_input"
        )
    
    with col2:
        search_btn = st.button("🚀 Ask", use_container_width=True)
    
    if search_btn and user_query:
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })
        
        with st.spinner("🔍 Searching codebase..."):
            try:
                lang = None if language == "All" else language.lower()
                response = requests.post(
                    f"{API_URL}/query",
                    json={"query": user_query, "language": lang, "top_k": 5},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': data['answer'],
                        'sources': data.get('sources', [])
                    })
                    st.session_state.total_queries += 1
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.rerun()

elif page == "📂 Ingest Repository":
    st.markdown("## 📂 Ingest GitHub Repository")
    
    st.markdown("""
    <div class="custom-card">
        <h3>🔄 Add a New Repository</h3>
        <p>Index a GitHub repository to enable code search and Q&A</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        repo_url = st.text_input(
            "Repository URL",
            placeholder="https://github.com/username/repo",
            label_visibility="collapsed"
        )
    
    with col2:
        branch = st.text_input("Branch", value="main")
    
    if st.button("🚀 Ingest Repository", use_container_width=True):
        if repo_url:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("🔄 Cloning and indexing repository..."):
                try:
                    status_text.text("Cloning repository...")
                    progress_bar.progress(20)
                    
                    response = requests.post(
                        f"{API_URL}/ingest",
                        json={"repo_url": repo_url, "branch": branch},
                        timeout=300
                    )
                    
                    progress_bar.progress(100)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.success(f"✅ Successfully ingested **{data['repo_name']}**!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Files", data['files_processed'])
                        with col2:
                            st.metric("Chunks", data['chunks_created'])
                        with col3:
                            st.metric("Indexed", data['chunks_indexed'])
                        
                        st.session_state.indexed_repos.append({
                            'name': data['repo_name'],
                            'url': repo_url,
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                    else:
                        st.error(f"Error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a repository URL")
    
    # Show indexed repositories
    if st.session_state.indexed_repos:
        st.markdown("---")
        st.markdown("### 📚 Indexed Repositories")
        
        for repo in st.session_state.indexed_repos:
            st.markdown(f"""
            <div class="source-card">
                <strong>{repo['name']}</strong><br>
                🔗 {repo['url']}<br>
                ⏰ {repo['time']}
            </div>
            """, unsafe_allow_html=True)

elif page == "💡 Explain Code":
    st.markdown("## 💡 Get AI Explanations")
    
    st.markdown("""
    <div class="custom-card">
        <h3>🧠 Code Analysis</h3>
        <p>Paste any code snippet and get an AI-powered explanation</p>
    </div>
    """, unsafe_allow_html=True)
    
    language = st.selectbox(
        "Language",
        ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript"]
    )
    
    code_input = st.text_area(
        "Code:",
        height=300,
        placeholder="def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
        label_visibility="collapsed"
    )
    
    if st.button("✨ Explain", use_container_width=True):
        if code_input:
            with st.spinner("🤔 Analyzing code..."):
                try:
                    response = requests.post(
                        f"{API_URL}/explain",
                        json={"code": code_input, "language": language.lower()},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.markdown("### 📖 Explanation")
                        st.markdown(f"""
                        <div class="assistant-message">
                            {data.get('explanation', 'No explanation available')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter some code")

elif page == "📊 Dashboard":
    st.markdown("## 📊 System Dashboard")
    
    stats = get_system_stats()
    health = health_data if health_data else {}
    
    # Main stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Indexed Vectors</div>
            <div class="stat-number">{stats.get('indexed_vectors', 0):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Queries</div>
            <div class="stat-number">{st.session_state.total_queries}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Dimension</div>
            <div class="stat-number">{stats.get('dimension', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 Chat Activity")
        if st.session_state.chat_history:
            user_msgs = len([m for m in st.session_state.chat_history if m['role'] == 'user'])
            ai_msgs = len([m for m in st.session_state.chat_history if m['role'] == 'assistant'])
            
            fig = go.Figure(data=[
                go.Bar(name='Your Questions', x=['Messages'], y=[user_msgs], marker_color='#667eea'),
                go.Bar(name='AI Responses', x=['Messages'], y=[ai_msgs], marker_color='#764ba2')
            ])
            fig.update_layout(barmode='group', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No chat history yet")
    
    with col2:
        st.markdown("### 📚 Repositories")
        if st.session_state.indexed_repos:
            repo_names = [r['name'] for r in st.session_state.indexed_repos]
            fig = go.Figure(data=[go.Pie(labels=repo_names, values=[1]*len(repo_names))])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No repositories indexed yet")
    
    # System Health
    st.markdown("---")
    st.markdown("### 🏥 System Health")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="custom-card">
            <h4>Status</h4>
            <p style="font-size: 1.5rem;">✅ {health.get('status', 'unknown').upper()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="custom-card">
            <h4>Version</h4>
            <p style="font-size: 1.5rem;">🚀 {health.get('version', '1.0.0')}</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem;">
    <strong>Codebase RAG</strong> v1.0.0 | Built with ❤️ using Streamlit & FastAPI<br>
    <small>Powered by AI | Semantic Code Search</small>
</div>
""", unsafe_allow_html=True)
