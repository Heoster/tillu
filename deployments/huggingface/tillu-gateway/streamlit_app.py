"""
TILLU Gateway - HuggingFace Spaces Deployment
Streamlit-based web interface for TILLU backend
"""

import streamlit as st
import httpx
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="TILLU - Personal AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_url" not in st.session_state:
    st.session_state.api_url = os.getenv("TILLU_API_URL", "http://localhost:8000")

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # API Configuration
    st.subheader("API Configuration")
    api_url = st.text_input(
        "API URL",
        value=st.session_state.api_url,
        help="TILLU backend API endpoint"
    )
    st.session_state.api_url = api_url
    
    # Test connection
    if st.button("🔗 Test Connection"):
        try:
            resp = httpx.get(f"{api_url}/health", timeout=5.0)
            if resp.status_code == 200:
                st.success("✅ Connected to TILLU backend")
            else:
                st.error(f"❌ API returned status {resp.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")
    
    st.divider()
    
    # About
    st.subheader("About TILLU")
    st.markdown("""
    **TILLU** - Personal AI Backend
    
    - 🧠 Semantic memory with pgvector
    - 🔄 Multi-provider LLM routing
    - 📊 Real-time event streaming
    - 🎯 Proactive intelligence
    
    [GitHub](https://github.com/Heoster/tillu)
    """)

# Main content
st.title("🧠 TILLU - Personal AI Backend")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📊 Memory", "🔧 Tools", "📈 Status"])

# Tab 1: Chat
with tab1:
    st.subheader("Conversational AI")
    
    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    user_input = st.chat_input("Ask TILLU something...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get response from API
        try:
            with st.spinner("Thinking..."):
                response = httpx.post(
                    f"{st.session_state.api_url}/api/gateway/chat",
                    json={"message": user_input},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assistant_response = data.get("response", "No response received")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    st.rerun()
                else:
                    st.error(f"API error: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Tab 2: Memory
with tab2:
    st.subheader("Semantic Memory")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Store Memory")
        memory_text = st.text_area("Memory content", height=150)
        memory_type = st.selectbox("Type", ["note", "event", "insight", "learning"])
        
        if st.button("💾 Save Memory"):
            try:
                response = httpx.post(
                    f"{st.session_state.api_url}/api/memory/store",
                    json={
                        "content": memory_text,
                        "type": memory_type,
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    st.success("✅ Memory saved")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("### 🔍 Search Memory")
        search_query = st.text_input("Search query")
        
        if search_query:
            try:
                response = httpx.get(
                    f"{st.session_state.api_url}/api/memory/search",
                    params={"query": search_query, "limit": 5},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results:
                        for result in results:
                            with st.expander(f"📌 {result.get('title', 'Memory')}"):
                                st.markdown(result.get("content", ""))
                                st.caption(f"Score: {result.get('score', 0):.2f}")
                    else:
                        st.info("No memories found")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Tab 3: Tools
with tab3:
    st.subheader("Available Tools")
    
    try:
        response = httpx.get(
            f"{st.session_state.api_url}/api/gateway/tools",
            timeout=10.0
        )
        
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            
            for tool in tools:
                with st.expander(f"🔧 {tool.get('name', 'Tool')}"):
                    st.markdown(f"**Description:** {tool.get('description', 'N/A')}")
                    
                    if tool.get("parameters"):
                        st.markdown("**Parameters:**")
                        for param, details in tool.get("parameters", {}).items():
                            st.markdown(f"- `{param}`: {details.get('description', 'N/A')}")
        else:
            st.error(f"Error: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Tab 4: Status
with tab4:
    st.subheader("System Status")
    
    col1, col2, col3 = st.columns(3)
    
    try:
        response = httpx.get(
            f"{st.session_state.api_url}/health",
            timeout=5.0
        )
        
        if response.status_code == 200:
            health = response.json()
            
            with col1:
                st.metric("API Status", "🟢 Online")
            
            with col2:
                st.metric("Version", health.get("version", "N/A"))
            
            with col3:
                st.metric("Uptime", "Running")
            
            st.divider()
            
            # Detailed status
            st.markdown("### 📊 Detailed Status")
            st.json(health)
        else:
            st.error("❌ API is offline")
    except Exception as e:
        st.error(f"❌ Cannot reach API: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    TILLU v0.1.0 | Deployed on HuggingFace Spaces | 
    <a href="https://github.com/Heoster/tillu">GitHub</a>
</div>
""", unsafe_allow_html=True)
