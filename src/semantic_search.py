"""
Semantic Search Module for StudyMate
Implements FAISS-based vector search with SentenceTransformers embeddings
"""

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import pickle
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """FAISS-based semantic search engine for document chunks"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        """
        Initialize the semantic search engine
        
        Args:
            model_name (str): SentenceTransformer model name
            dimension (int): Embedding dimension
        """
        self.model_name = model_name
        self.dimension = dimension
        self.model = None
        self.index = None
        self.chunks = []
        self.embeddings = None
        
        self._load_model()
        self._initialize_index()
    
    def _load_model(self):
        """Load the SentenceTransformer model"""
        try:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise e
    
    def _initialize_index(self):
        """Initialize FAISS index"""
        try:
            # Use IndexFlatIP for cosine similarity (after L2 normalization)
            self.index = faiss.IndexFlatIP(self.dimension)
            logger.info(f"FAISS index initialized with dimension {self.dimension}")
        except Exception as e:
            logger.error(f"Error initializing FAISS index: {str(e)}")
            raise e
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts into embeddings
        
        Args:
            texts (List[str]): List of text strings
            
        Returns:
            np.ndarray: Array of embeddings
        """
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding texts: {str(e)}")
            raise e
    
    def build_index(self, chunks: List[Dict[str, any]]):
        """
        Build FAISS index from document chunks
        
        Args:
            chunks (List[Dict]): List of text chunks with metadata
        """
        try:
            logger.info(f"Building index from {len(chunks)} chunks")
            
            # Extract text from chunks
            texts = [chunk['text'] for chunk in chunks]
            
            # Generate embeddings
            self.embeddings = self.encode_texts(texts)
            
            # Add to FAISS index
            self.index.add(self.embeddings.astype('float32'))
            
            # Store chunks for retrieval
            self.chunks = chunks
            
            logger.info(f"Index built successfully with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            raise e
    
    def search(self, query: str, k: int = 5, score_threshold: float = 0.3) -> List[Dict[str, any]]:
        """
        Search for similar chunks using semantic similarity
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            score_threshold (float): Minimum similarity score
            
        Returns:
            List[Dict]: List of similar chunks with scores
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Index is empty")
                return []
            
            # Encode query
            query_embedding = self.encode_texts([query])
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1 and score >= score_threshold:
                    chunk = self.chunks[idx].copy()
                    chunk['similarity_score'] = float(score)
                    chunk['rank'] = i + 1
                    results.append(chunk)
            
            logger.info(f"Found {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def save_index(self, filepath: str):
        """
        Save FAISS index and metadata to disk
        
        Args:
            filepath (str): Path to save the index
        """
        try:
            # Save FAISS index
            faiss.write_index(self.index, f"{filepath}.faiss")
            
            # Save metadata
            metadata = {
                'chunks': self.chunks,
                'model_name': self.model_name,
                'dimension': self.dimension,
                'embeddings': self.embeddings
            }
            
            with open(f"{filepath}.pkl", 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Index saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise e
    
    def load_index(self, filepath: str):
        """
        Load FAISS index and metadata from disk
        
        Args:
            filepath (str): Path to load the index from
        """
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{filepath}.faiss")
            
            # Load metadata
            with open(f"{filepath}.pkl", 'rb') as f:
                metadata = pickle.load(f)
            
            self.chunks = metadata['chunks']
            self.embeddings = metadata['embeddings']
            
            # Verify model compatibility
            if metadata['model_name'] != self.model_name:
                logger.warning(f"Model mismatch: loaded {metadata['model_name']}, current {self.model_name}")
            
            logger.info(f"Index loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise e
    
    def get_context_window(self, chunks: List[Dict[str, any]], window_size: int = 2) -> List[Dict[str, any]]:
        """
        Expand retrieved chunks with surrounding context
        
        Args:
            chunks (List[Dict]): Retrieved chunks
            window_size (int): Number of chunks to include before/after
            
        Returns:
            List[Dict]: Expanded chunks with context
        """
        if not chunks:
            return []
        
        # Get all chunk IDs and sort by position
        chunk_ids = [chunk['id'] for chunk in chunks]
        all_chunk_ids = list(range(len(self.chunks)))
        
        expanded_ids = set()
        
        for chunk_id in chunk_ids:
            # Add the chunk itself
            expanded_ids.add(chunk_id)
            
            # Add surrounding chunks
            for i in range(max(0, chunk_id - window_size), 
                          min(len(self.chunks), chunk_id + window_size + 1)):
                expanded_ids.add(i)
        
        # Get expanded chunks
        expanded_chunks = []
        for chunk_id in sorted(expanded_ids):
            chunk = self.chunks[chunk_id].copy()
            chunk['is_context'] = chunk_id not in chunk_ids
            expanded_chunks.append(chunk)
        
        return expanded_chunks
    
    def get_stats(self) -> Dict[str, any]:
        """Get search engine statistics"""
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'total_chunks': len(self.chunks),
            'index_size': self.index.ntotal if self.index else 0,
            'is_trained': self.index.is_trained if self.index else False
        }


class DocumentStore:
    """Manages multiple documents and their search indices"""
    
    def __init__(self, storage_path: str = "/workspace/data"):
        self.storage_path = storage_path
        self.documents = {}
        self.search_engines = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
    
    def add_document(self, doc_id: str, chunks: List[Dict[str, any]], 
                    metadata: Dict[str, any] = None):
        """
        Add a document to the store
        
        Args:
            doc_id (str): Unique document identifier
            chunks (List[Dict]): Document chunks
            metadata (Dict): Document metadata
        """
        try:
            # Create search engine for this document
            search_engine = SemanticSearchEngine()
            search_engine.build_index(chunks)
            
            # Store document info
            self.documents[doc_id] = {
                'chunks': chunks,
                'metadata': metadata or {},
                'created_at': np.datetime64('now')
            }
            
            self.search_engines[doc_id] = search_engine
            
            # Save to disk
            search_engine.save_index(os.path.join(self.storage_path, doc_id))
            
            logger.info(f"Document {doc_id} added to store")
            
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {str(e)}")
            raise e
    
    def search_document(self, doc_id: str, query: str, k: int = 5) -> List[Dict[str, any]]:
        """Search within a specific document"""
        if doc_id not in self.search_engines:
            logger.warning(f"Document {doc_id} not found")
            return []
        
        return self.search_engines[doc_id].search(query, k)
    
    def search_all_documents(self, query: str, k: int = 5) -> Dict[str, List[Dict[str, any]]]:
        """Search across all documents"""
        results = {}
        
        for doc_id, search_engine in self.search_engines.items():
            doc_results = search_engine.search(query, k)
            if doc_results:
                results[doc_id] = doc_results
        
        return results
    
    def get_document_list(self) -> List[Dict[str, any]]:
        """Get list of all documents"""
        doc_list = []
        
        for doc_id, doc_info in self.documents.items():
            doc_list.append({
                'id': doc_id,
                'metadata': doc_info['metadata'],
                'chunk_count': len(doc_info['chunks']),
                'created_at': str(doc_info['created_at'])
            })
        
        return doc_list


if __name__ == "__main__":
    # Test the semantic search engine
    search_engine = SemanticSearchEngine()
    print("Semantic Search Engine initialized successfully!")
    print(f"Model: {search_engine.model_name}")
    print(f"Dimension: {search_engine.dimension}")