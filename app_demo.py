"""
StudyMate Demo - Simplified version without heavy dependencies
This demonstrates the UI and basic functionality
"""

import streamlit as st
import os
import tempfile
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="StudyMate - AI Study Assistant (Demo)",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .document-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .question-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    
    .answer-box {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    
    .demo-notice {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None


def display_header():
    """Display the main header"""
    st.markdown('<div class="main-header">📚 StudyMate (Demo)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered PDF-Based Q&A System for Students</div>', unsafe_allow_html=True)
    
    # Demo notice
    st.markdown("""
    <div class="demo-notice">
        <strong>🚀 Demo Mode:</strong> This is a demonstration version showing the UI and basic functionality. 
        The full version includes PDF processing, semantic search, and AI-powered answer generation.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")


def sidebar_document_management():
    """Sidebar for document management"""
    st.sidebar.header("📄 Document Management")
    
    # Upload new document
    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF Document",
        type=['pdf'],
        help="Upload a PDF document to start asking questions (Demo: File will be processed but not analyzed)"
    )
    
    if uploaded_file is not None:
        # Simulate document processing
        with st.sidebar.spinner("Processing document..."):
            import time
            time.sleep(2)  # Simulate processing time
            
            # Add to session state
            doc_info = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'uploaded_at': datetime.now().isoformat(),
                'id': f"doc_{len(st.session_state.uploaded_files)}"
            }
            
            if doc_info not in st.session_state.uploaded_files:
                st.session_state.uploaded_files.append(doc_info)
                st.session_state.current_document = doc_info['id']
            
            st.sidebar.success(f"✅ Document '{uploaded_file.name}' processed successfully!")
            st.sidebar.info(f"""
            **Document Info (Simulated):**
            - Size: {uploaded_file.size} bytes
            - Pages: ~{max(1, uploaded_file.size // 2000)}
            - Text Chunks: ~{max(5, uploaded_file.size // 500)}
            """)
    
    # Display available documents
    if st.session_state.uploaded_files:
        st.sidebar.subheader("Available Documents")
        
        for doc in st.session_state.uploaded_files:
            is_current = doc['id'] == st.session_state.current_document
            
            with st.sidebar.container():
                col1, col2 = st.sidebar.columns([3, 1])
                
                with col1:
                    title = doc['name']
                    if len(title) > 30:
                        title = title[:30] + "..."
                    
                    if is_current:
                        st.markdown(f"**🔵 {title}**")
                    else:
                        st.markdown(f"📄 {title}")
                    
                    st.caption(f"Size: {doc['size']} bytes")
                
                with col2:
                    if st.button("Select", key=f"select_{doc['id']}"):
                        st.session_state.current_document = doc['id']
                        st.rerun()
    
    # System statistics
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 System Stats")
    
    st.sidebar.metric("Total Documents", len(st.session_state.uploaded_files))
    st.sidebar.metric("Conversations", len(st.session_state.conversation_history))
    st.sidebar.metric("Status", "Demo Mode")
    
    # Clear conversation button
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.conversation_history = []
        st.rerun()


def display_qa_interface():
    """Display the main Q&A interface"""
    if not st.session_state.uploaded_files:
        st.info("👆 Please upload a PDF document to start asking questions.")
        
        # Show demo features
        st.subheader("🌟 StudyMate Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📄 PDF Processing**
            - Extract text from academic PDFs
            - Handle complex layouts and figures
            - Chunk text for optimal search
            - Preserve document metadata
            """)
            
            st.markdown("""
            **🔍 Semantic Search**
            - FAISS-based vector similarity
            - SentenceTransformers embeddings
            - Context-aware retrieval
            - Relevance scoring
            """)
        
        with col2:
            st.markdown("""
            **🤖 AI Answer Generation**
            - IBM Watson Mixtral-8x7B model
            - Context-grounded responses
            - Source attribution
            - Follow-up suggestions
            """)
            
            st.markdown("""
            **💬 Interactive Interface**
            - Streamlit-based UI
            - Document management
            - Conversation history
            - Real-time processing
            """)
        
        return
    
    # Question input
    st.subheader("🤔 Ask a Question")
    
    # Get current document info
    current_doc = None
    for doc in st.session_state.uploaded_files:
        if doc['id'] == st.session_state.current_document:
            current_doc = doc
            break
    
    if current_doc:
        st.info(f"📄 Current document: **{current_doc['name']}**")
    
    # Quick question suggestions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize this document"):
            question = "Can you provide a comprehensive summary of this document?"
            process_demo_question(question)
    
    with col2:
        if st.button("🔍 What are the main topics?"):
            question = "What are the main topics and concepts covered in this document?"
            process_demo_question(question)
    
    # Main question input
    question = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="Ask anything about your uploaded document..."
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 Ask Question", type="primary", disabled=not question.strip()):
            if question.strip():
                process_demo_question(question.strip())
    
    with col2:
        max_chunks = st.selectbox("Max Context", [3, 5, 7, 10], index=1)
    
    with col3:
        if st.button("🔍 Search Only"):
            if question.strip():
                demo_search(question.strip())


def process_demo_question(question: str):
    """Process a question and display demo answer"""
    with st.spinner("🤔 Thinking... (Demo Mode)"):
        import time
        time.sleep(2)  # Simulate processing time
        
        # Generate demo answer based on question
        demo_answers = {
            "summary": "This document appears to cover fundamental concepts in artificial intelligence and machine learning. The main sections include an introduction to AI principles, supervised and unsupervised learning algorithms, neural networks, and practical applications in various domains. The document emphasizes both theoretical foundations and practical implementation approaches.",
            "topics": "The main topics covered in this document include: 1) Introduction to Artificial Intelligence, 2) Machine Learning Fundamentals, 3) Supervised Learning Algorithms, 4) Unsupervised Learning Techniques, 5) Neural Networks and Deep Learning, 6) Natural Language Processing, 7) Computer Vision Applications, and 8) Ethical Considerations in AI.",
            "default": f"Based on the content of the uploaded document, here's what I found regarding your question: '{question}'. The document discusses relevant concepts and provides detailed explanations that address your inquiry. Key points include theoretical foundations, practical applications, and supporting examples that illustrate the main concepts."
        }
        
        # Determine answer type
        if "summary" in question.lower() or "summarize" in question.lower():
            answer = demo_answers["summary"]
        elif "topic" in question.lower() or "main" in question.lower():
            answer = demo_answers["topics"]
        else:
            answer = demo_answers["default"]
        
        # Display question and answer
        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        st.markdown(f"**❓ Question:** {question}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown(f"**🤖 Answer (Demo):**")
        st.markdown(answer)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display demo sources
        st.markdown("**📚 Sources (Demo):**")
        demo_sources = [
            {"chunk_id": 1, "similarity_score": 0.87, "text_preview": "Artificial intelligence represents a broad field of study focused on creating intelligent systems..."},
            {"chunk_id": 2, "similarity_score": 0.82, "text_preview": "Machine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning..."},
            {"chunk_id": 3, "similarity_score": 0.78, "text_preview": "Neural networks form the backbone of deep learning approaches and have shown remarkable success..."}
        ]
        
        for i, source in enumerate(demo_sources, 1):
            with st.expander(f"Source {i} (Similarity: {source['similarity_score']:.2f})"):
                st.markdown(source['text_preview'])
        
        # Display follow-up questions
        st.markdown("**💡 Follow-up Questions (Demo):**")
        follow_ups = [
            "Can you explain the differences between supervised and unsupervised learning?",
            "What are some practical applications of these concepts?",
            "How do neural networks work in this context?"
        ]
        
        for i, follow_up in enumerate(follow_ups, 1):
            if st.button(f"{i}. {follow_up}", key=f"followup_{i}_{len(st.session_state.conversation_history)}"):
                process_demo_question(follow_up)
        
        # Display metadata
        with st.expander("ℹ️ Response Details (Demo)"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Context Chunks", 3)
            with col2:
                st.metric("Model", "Demo Mode")
            with col3:
                st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
        
        # Update conversation history
        st.session_state.conversation_history.append({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'mode': 'demo'
        })


def demo_search(query: str):
    """Demo search functionality"""
    with st.spinner("🔍 Searching... (Demo Mode)"):
        import time
        time.sleep(1)
        
        st.markdown(f"**🔍 Search Results (Demo) for:** {query}")
        
        demo_results = [
            {"text": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from and make predictions on data.", "score": 0.89},
            {"text": "Supervised learning algorithms require labeled training data to learn patterns and make predictions on new, unseen data.", "score": 0.84},
            {"text": "Neural networks are computing systems inspired by biological neural networks and form the foundation of deep learning.", "score": 0.79}
        ]
        
        for i, match in enumerate(demo_results, 1):
            st.markdown(f"**Match {i}** (Score: {match['score']:.2f})")
            st.markdown(match['text'])
            st.markdown("---")


def display_conversation_history():
    """Display conversation history"""
    if st.session_state.conversation_history:
        st.subheader("💬 Conversation History")
        
        for i, item in enumerate(reversed(st.session_state.conversation_history), 1):
            with st.expander(f"Q{len(st.session_state.conversation_history)-i+1}: {item['question'][:50]}..."):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Answer:** {item['answer']}")
                st.caption(f"Time: {item['timestamp']} | Mode: {item.get('mode', 'demo')}")
    else:
        st.info("No conversation history yet. Ask a question to get started!")


def display_system_info():
    """Display system information and instructions"""
    st.subheader("🔧 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Current Status:** Demo Mode
        
        **Available Features:**
        - ✅ Document upload simulation
        - ✅ Question interface
        - ✅ Demo answer generation
        - ✅ Conversation history
        - ✅ Search simulation
        
        **Full Version Features:**
        - 🔄 Real PDF text extraction
        - 🔄 Semantic vector search
        - 🔄 AI-powered answers
        - 🔄 Source attribution
        """)
    
    with col2:
        st.markdown("""
        **Technology Stack:**
        - **Frontend:** Streamlit
        - **PDF Processing:** PyMuPDF
        - **Search:** FAISS + SentenceTransformers
        - **AI Model:** IBM Watson Mixtral-8x7B
        - **Language:** Python 3.8+
        
        **To Enable Full Features:**
        1. Install dependencies: `pip install -r requirements.txt`
        2. Configure IBM Watson credentials
        3. Run: `python run_app.py`
        """)


def main():
    """Main application function"""
    initialize_session_state()
    
    display_header()
    
    # Sidebar
    sidebar_document_management()
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🤔 Ask Questions", "💬 History", "🔧 System Info", "📖 About"])
    
    with tab1:
        display_qa_interface()
    
    with tab2:
        display_conversation_history()
    
    with tab3:
        display_system_info()
    
    with tab4:
        st.markdown("""
        ## 📖 About StudyMate
        
        StudyMate is an AI-powered PDF-based Q&A system designed to help students interact with their study materials more effectively.
        
        ### 🎯 Purpose
        Instead of passively reading large PDF documents, students can:
        - Upload textbooks, research papers, and lecture notes
        - Ask natural-language questions about the content
        - Get contextual, AI-generated answers with source references
        - Explore topics through follow-up questions
        
        ### 🛠️ How It Works
        1. **PDF Processing:** Extract and chunk text from uploaded documents
        2. **Semantic Search:** Use FAISS and embeddings to find relevant content
        3. **AI Generation:** Generate answers using IBM Watson's Mixtral model
        4. **Interactive UI:** Present results in a user-friendly interface
        
        ### 🚀 Getting Started
        1. Upload a PDF document using the sidebar
        2. Ask questions about the content
        3. Explore the AI-generated answers and sources
        4. Use follow-up questions to dive deeper
        
        **This demo shows the interface and basic functionality. The full version includes real PDF processing and AI-powered answers.**
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**StudyMate Demo** - AI-Powered PDF-Based Q&A System | "
        "Built with Streamlit, FAISS, SentenceTransformers, and IBM Watson"
    )


if __name__ == "__main__":
    main()