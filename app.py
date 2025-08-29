"""
StudyMate - AI-Powered PDF-Based Q&A System
Streamlit Frontend Application
"""

import streamlit as st
import os
import sys
from datetime import datetime
import tempfile
from typing import Dict, List

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from qa_system import StudyMateQASystem

# Page configuration
st.set_page_config(
    page_title="StudyMate - AI Study Assistant",
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
    
    .source-box {
        background-color: #fff3e0;
        border: 1px solid #ffb74d;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    
    .stats-metric {
        text-align: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = StudyMateQASystem(use_watson=False)  # Default to fallback
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = []


def display_header():
    """Display the main header"""
    st.markdown('<div class="main-header">📚 StudyMate</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered PDF-Based Q&A System for Students</div>', unsafe_allow_html=True)
    
    st.markdown("---")


def sidebar_document_management():
    """Sidebar for document management"""
    st.sidebar.header("📄 Document Management")
    
    # Upload new document
    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF Document",
        type=['pdf'],
        help="Upload a PDF document to start asking questions"
    )
    
    if uploaded_file is not None:
        with st.sidebar.spinner("Processing document..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            
            try:
                # Process the document
                result = st.session_state.qa_system.upload_document(
                    tmp_file_path, 
                    document_title=uploaded_file.name
                )
                
                if result['success']:
                    st.sidebar.success(f"✅ {result['message']}")
                    
                    if result['is_new']:
                        st.sidebar.info(f"""
                        **Document Info:**
                        - Title: {result['title']}
                        - Pages: {result['page_count']}
                        - Text Chunks: {result['chunk_count']}
                        """)
                    
                    # Update session state
                    st.session_state.current_document = result['document_id']
                    st.session_state.uploaded_documents = st.session_state.qa_system.get_available_documents()
                    
                else:
                    st.sidebar.error(f"❌ {result['message']}")
                    
            except Exception as e:
                st.sidebar.error(f"Error processing document: {str(e)}")
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
    
    # Display available documents
    available_docs = st.session_state.qa_system.get_available_documents()
    
    if available_docs:
        st.sidebar.subheader("Available Documents")
        
        for doc in available_docs:
            is_current = doc['id'] == st.session_state.current_document
            
            with st.sidebar.container():
                col1, col2 = st.sidebar.columns([3, 1])
                
                with col1:
                    title = doc['metadata'].get('title', 'Unknown')
                    if len(title) > 30:
                        title = title[:30] + "..."
                    
                    if is_current:
                        st.markdown(f"**🔵 {title}**")
                    else:
                        st.markdown(f"📄 {title}")
                    
                    st.caption(f"Chunks: {doc['chunk_count']}")
                
                with col2:
                    if st.button("Select", key=f"select_{doc['id']}"):
                        result = st.session_state.qa_system.select_document(doc['id'])
                        if result['success']:
                            st.session_state.current_document = doc['id']
                            st.rerun()
                        else:
                            st.error(result['message'])
    
    # System statistics
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 System Stats")
    
    stats = st.session_state.qa_system.get_system_stats()
    st.sidebar.metric("Total Documents", stats.get('total_documents', 0))
    st.sidebar.metric("Total Chunks", stats.get('total_chunks', 0))
    st.sidebar.metric("Conversations", stats.get('conversation_history_length', 0))
    
    # Clear conversation button
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.qa_system.clear_conversation_history()
        st.session_state.conversation_history = []
        st.rerun()


def display_document_summary():
    """Display current document summary"""
    if st.session_state.current_document:
        with st.expander("📋 Document Summary", expanded=False):
            with st.spinner("Generating summary..."):
                summary_result = st.session_state.qa_system.get_document_summary(
                    st.session_state.current_document
                )
                
                if summary_result['success']:
                    st.markdown(f"**Title:** {summary_result['title']}")
                    
                    metadata = summary_result['metadata']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Pages", metadata.get('page_count', 'Unknown'))
                    with col2:
                        st.metric("Author", metadata.get('author', 'Unknown'))
                    with col3:
                        st.metric("Chunks", summary_result['total_chunks'])
                    
                    st.markdown("**Summary:**")
                    st.markdown(summary_result['summary'])
                else:
                    st.error(f"Error generating summary: {summary_result.get('message', 'Unknown error')}")


def display_qa_interface():
    """Display the main Q&A interface"""
    if not st.session_state.current_document:
        st.info("👆 Please upload and select a PDF document to start asking questions.")
        return
    
    # Question input
    st.subheader("🤔 Ask a Question")
    
    # Quick question suggestions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize this document"):
            question = "Can you provide a comprehensive summary of this document?"
            process_question(question)
    
    with col2:
        if st.button("🔍 What are the main topics?"):
            question = "What are the main topics and concepts covered in this document?"
            process_question(question)
    
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
                process_question(question.strip())
    
    with col2:
        max_chunks = st.selectbox("Max Context", [3, 5, 7, 10], index=1)
    
    with col3:
        if st.button("🔍 Search Only"):
            if question.strip():
                search_documents(question.strip())


def process_question(question: str, max_chunks: int = 5):
    """Process a question and display the answer"""
    with st.spinner("🤔 Thinking..."):
        result = st.session_state.qa_system.ask_question(
            question, 
            max_context_chunks=max_chunks
        )
        
        if result['success']:
            # Display question and answer
            st.markdown('<div class="question-box">', unsafe_allow_html=True)
            st.markdown(f"**❓ Question:** {result['question']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown(f"**🤖 Answer:**")
            st.markdown(result['answer'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display sources
            if result.get('sources'):
                st.markdown("**📚 Sources:**")
                for i, source in enumerate(result['sources'], 1):
                    with st.expander(f"Source {i} (Similarity: {source['similarity_score']:.2f})"):
                        st.markdown(source['text_preview'])
            
            # Display follow-up questions
            if result.get('follow_up_questions'):
                st.markdown("**💡 Follow-up Questions:**")
                for i, follow_up in enumerate(result['follow_up_questions'], 1):
                    if st.button(f"{i}. {follow_up}", key=f"followup_{i}_{len(st.session_state.conversation_history)}"):
                        process_question(follow_up)
            
            # Display metadata
            with st.expander("ℹ️ Response Details"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Context Chunks", result['context_chunks_used'])
                with col2:
                    st.metric("Model", result['model_used'])
                with col3:
                    st.metric("Timestamp", result['timestamp'].split('T')[1][:8])
            
            # Update conversation history
            st.session_state.conversation_history.append({
                'question': question,
                'answer': result['answer'],
                'timestamp': result['timestamp']
            })
            
        else:
            st.error(f"❌ {result['message']}")
            if 'error' in result:
                st.error(f"Error details: {result['error']}")


def search_documents(query: str):
    """Search documents and display results"""
    with st.spinner("🔍 Searching..."):
        result = st.session_state.qa_system.search_documents(
            query, 
            document_id=st.session_state.current_document
        )
        
        if result['success'] and result['results']:
            st.markdown(f"**🔍 Search Results for:** {query}")
            
            for doc_id, matches in result['results'].items():
                st.markdown(f"**Document:** {doc_id}")
                
                for i, match in enumerate(matches, 1):
                    st.markdown('<div class="source-box">', unsafe_allow_html=True)
                    st.markdown(f"**Match {i}** (Score: {match['similarity_score']:.2f})")
                    st.markdown(match['text'][:300] + "..." if len(match['text']) > 300 else match['text'])
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No relevant passages found.")


def display_conversation_history():
    """Display conversation history"""
    history = st.session_state.qa_system.get_conversation_history()
    
    if history:
        st.subheader("💬 Conversation History")
        
        for i, item in enumerate(reversed(history), 1):
            with st.expander(f"Q{len(history)-i+1}: {item['question'][:50]}..."):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Answer:** {item['answer']}")
                st.caption(f"Time: {item['timestamp']}")


def main():
    """Main application function"""
    initialize_session_state()
    
    display_header()
    
    # Sidebar
    sidebar_document_management()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🤔 Ask Questions", "📋 Document Summary", "💬 History"])
    
    with tab1:
        display_qa_interface()
    
    with tab2:
        display_document_summary()
    
    with tab3:
        display_conversation_history()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**StudyMate** - AI-Powered PDF-Based Q&A System | "
        "Built with Streamlit, FAISS, SentenceTransformers, and IBM Watson"
    )


if __name__ == "__main__":
    main()