"""
Main Q&A System for StudyMate
Orchestrates PDF processing, semantic search, and answer generation
"""

import os
import hashlib
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

from pdf_processor import PDFProcessor
from semantic_search import SemanticSearchEngine, DocumentStore
from llm_integration import LLMAnswerGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StudyMateQASystem:
    """Main Q&A system that orchestrates all components"""
    
    def __init__(self, data_path: str = "/workspace/data", use_watson: bool = True):
        """
        Initialize the StudyMate Q&A System
        
        Args:
            data_path (str): Path to store data and indices
            use_watson (bool): Whether to use IBM Watson for LLM
        """
        self.data_path = data_path
        self.uploads_path = "/workspace/uploads"
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.document_store = DocumentStore(data_path)
        self.answer_generator = LLMAnswerGenerator(use_watson=use_watson)
        
        # Create directories
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(self.uploads_path, exist_ok=True)
        
        # Session state
        self.current_document = None
        self.conversation_history = []
        
        logger.info("StudyMate Q&A System initialized successfully")
    
    def _generate_document_id(self, filepath: str) -> str:
        """Generate unique document ID based on file content"""
        try:
            with open(filepath, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            filename = os.path.basename(filepath)
            return f"{filename}_{file_hash[:8]}"
        except Exception as e:
            logger.error(f"Error generating document ID: {str(e)}")
            return f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def upload_document(self, pdf_path: str, document_title: str = None) -> Dict[str, any]:
        """
        Upload and process a PDF document
        
        Args:
            pdf_path (str): Path to the PDF file
            document_title (str): Optional title for the document
            
        Returns:
            Dict: Processing results and document info
        """
        try:
            logger.info(f"Processing document: {pdf_path}")
            
            # Generate document ID
            doc_id = self._generate_document_id(pdf_path)
            
            # Check if document already exists
            existing_docs = self.document_store.get_document_list()
            if any(doc['id'] == doc_id for doc in existing_docs):
                logger.info(f"Document {doc_id} already exists")
                self.current_document = doc_id
                return {
                    'success': True,
                    'document_id': doc_id,
                    'message': 'Document already processed',
                    'is_new': False
                }
            
            # Extract metadata
            metadata = self.pdf_processor.get_document_metadata(pdf_path)
            if document_title:
                metadata['title'] = document_title
            
            # Process PDF
            full_text, chunks = self.pdf_processor.process_pdf(pdf_path)
            
            # Add to document store
            self.document_store.add_document(doc_id, chunks, metadata)
            
            # Set as current document
            self.current_document = doc_id
            
            # Clear conversation history for new document
            self.conversation_history = []
            
            result = {
                'success': True,
                'document_id': doc_id,
                'title': metadata.get('title', 'Unknown'),
                'author': metadata.get('author', 'Unknown'),
                'page_count': metadata.get('page_count', 0),
                'chunk_count': len(chunks),
                'total_characters': len(full_text),
                'message': 'Document processed successfully',
                'is_new': True
            }
            
            logger.info(f"Document {doc_id} processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process document'
            }
    
    def ask_question(self, question: str, document_id: str = None, 
                    max_context_chunks: int = 5) -> Dict[str, any]:
        """
        Ask a question about the uploaded document(s)
        
        Args:
            question (str): User's question
            document_id (str): Specific document ID (uses current if None)
            max_context_chunks (int): Maximum context chunks to retrieve
            
        Returns:
            Dict: Answer with sources and metadata
        """
        try:
            # Use current document if none specified
            if document_id is None:
                document_id = self.current_document
            
            if document_id is None:
                return {
                    'success': False,
                    'message': 'No document selected. Please upload a document first.',
                    'question': question
                }
            
            logger.info(f"Processing question: {question[:50]}...")
            
            # Search for relevant context
            context_chunks = self.document_store.search_document(
                document_id, question, k=max_context_chunks
            )
            
            if not context_chunks:
                return {
                    'success': False,
                    'message': 'No relevant information found in the document.',
                    'question': question,
                    'document_id': document_id
                }
            
            # Get document metadata
            doc_list = self.document_store.get_document_list()
            doc_metadata = next((doc for doc in doc_list if doc['id'] == document_id), {})
            doc_title = doc_metadata.get('metadata', {}).get('title', 'Document')
            
            # Generate answer
            answer_result = self.answer_generator.generate_answer(
                question, context_chunks, doc_title
            )
            
            # Generate follow-up questions
            follow_ups = self.answer_generator.generate_follow_up_questions(
                question, answer_result.get('answer', ''), context_chunks
            )
            
            # Prepare final result
            result = {
                'success': True,
                'question': question,
                'answer': answer_result.get('answer', ''),
                'document_id': document_id,
                'document_title': doc_title,
                'sources': answer_result.get('sources', []),
                'context_chunks_used': len(context_chunks),
                'follow_up_questions': follow_ups,
                'model_used': answer_result.get('model_used', 'Unknown'),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to conversation history
            self.conversation_history.append({
                'question': question,
                'answer': result['answer'],
                'timestamp': result['timestamp'],
                'document_id': document_id
            })
            
            logger.info(f"Question answered successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process question',
                'question': question
            }
    
    def search_documents(self, query: str, document_id: str = None) -> Dict[str, any]:
        """
        Search for relevant passages in document(s)
        
        Args:
            query (str): Search query
            document_id (str): Specific document ID (searches all if None)
            
        Returns:
            Dict: Search results
        """
        try:
            if document_id:
                # Search specific document
                results = self.document_store.search_document(document_id, query)
                search_results = {document_id: results} if results else {}
            else:
                # Search all documents
                search_results = self.document_store.search_all_documents(query)
            
            return {
                'success': True,
                'query': query,
                'results': search_results,
                'total_documents_searched': len(search_results),
                'total_matches': sum(len(matches) for matches in search_results.values())
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def get_document_summary(self, document_id: str = None, max_chunks: int = 10) -> Dict[str, any]:
        """
        Generate a summary of the document
        
        Args:
            document_id (str): Document ID (uses current if None)
            max_chunks (int): Maximum chunks to include in summary
            
        Returns:
            Dict: Document summary
        """
        try:
            if document_id is None:
                document_id = self.current_document
            
            if document_id is None:
                return {
                    'success': False,
                    'message': 'No document selected'
                }
            
            # Get document info
            doc_list = self.document_store.get_document_list()
            doc_info = next((doc for doc in doc_list if doc['id'] == document_id), None)
            
            if not doc_info:
                return {
                    'success': False,
                    'message': 'Document not found'
                }
            
            # Get document chunks for summary
            chunks = self.document_store.documents[document_id]['chunks'][:max_chunks]
            
            # Generate summary
            doc_title = doc_info['metadata'].get('title', 'Document')
            summary = self.answer_generator.summarize_document_section(chunks, doc_title)
            
            return {
                'success': True,
                'document_id': document_id,
                'title': doc_title,
                'summary': summary,
                'metadata': doc_info['metadata'],
                'chunks_used': len(chunks),
                'total_chunks': doc_info['chunk_count']
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_available_documents(self) -> List[Dict[str, any]]:
        """Get list of all available documents"""
        return self.document_store.get_document_list()
    
    def select_document(self, document_id: str) -> Dict[str, any]:
        """
        Select a document as the current active document
        
        Args:
            document_id (str): Document ID to select
            
        Returns:
            Dict: Selection result
        """
        try:
            doc_list = self.get_available_documents()
            doc_info = next((doc for doc in doc_list if doc['id'] == document_id), None)
            
            if not doc_info:
                return {
                    'success': False,
                    'message': 'Document not found'
                }
            
            self.current_document = document_id
            self.clear_conversation_history()  # Clear history when switching documents
            
            return {
                'success': True,
                'document_id': document_id,
                'title': doc_info['metadata'].get('title', 'Unknown'),
                'message': 'Document selected successfully'
            }
            
        except Exception as e:
            logger.error(f"Error selecting document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_system_stats(self) -> Dict[str, any]:
        """Get system statistics"""
        try:
            doc_list = self.get_available_documents()
            
            return {
                'total_documents': len(doc_list),
                'current_document': self.current_document,
                'conversation_history_length': len(self.conversation_history),
                'total_chunks': sum(doc['chunk_count'] for doc in doc_list),
                'model_info': {
                    'using_watson': self.answer_generator.use_watson,
                    'model_name': 'IBM Watson Mixtral-8x7B' if self.answer_generator.use_watson else 'Fallback Model'
                },
                'storage_path': self.data_path
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {'error': str(e)}


if __name__ == "__main__":
    # Test the Q&A system
    qa_system = StudyMateQASystem(use_watson=False)  # Use fallback for testing
    print("StudyMate Q&A System initialized successfully!")
    
    stats = qa_system.get_system_stats()
    print(f"System stats: {stats}")