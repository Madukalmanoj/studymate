"""
PDF Processing Module for StudyMate
Handles PDF text extraction and preprocessing using PyMuPDF
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction and preprocessing"""
    
    def __init__(self):
        self.chunk_size = 500  # characters per chunk
        self.overlap = 50      # character overlap between chunks
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file using PyMuPDF
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
                
            doc.close()
            logger.info(f"Successfully extracted text from {pdf_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise e
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess extracted text
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned and preprocessed text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Remove page numbers and headers/footers (basic heuristic)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines (likely page numbers or artifacts)
            if len(line) > 10:
                cleaned_lines.append(line)
        
        text = ' '.join(cleaned_lines)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks for better semantic search
        
        Args:
            text (str): Preprocessed text
            
        Returns:
            List[Dict]: List of text chunks with metadata
        """
        chunks = []
        text_length = len(text)
        start = 0
        chunk_id = 0
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at sentence boundaries
            if end < text_length:
                # Look for sentence endings within the last 100 characters
                last_period = text.rfind('.', start, end)
                last_exclamation = text.rfind('!', start, end)
                last_question = text.rfind('?', start, end)
                
                sentence_end = max(last_period, last_exclamation, last_question)
                
                if sentence_end > start + (self.chunk_size // 2):
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'length': len(chunk_text)
                })
                chunk_id += 1
            
            # Move start position with overlap
            start = max(start + self.chunk_size - self.overlap, end)
        
        logger.info(f"Created {len(chunks)} text chunks")
        return chunks
    
    def process_pdf(self, pdf_path: str) -> Tuple[str, List[Dict[str, any]]]:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Tuple[str, List[Dict]]: Full text and list of chunks
        """
        # Extract text
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        # Preprocess text
        clean_text = self.preprocess_text(raw_text)
        
        # Create chunks
        chunks = self.chunk_text(clean_text)
        
        return clean_text, chunks
    
    def get_document_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract metadata from PDF document
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Dict: Document metadata
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            
            return {
                'title': metadata.get('title', 'Unknown'),
                'author': metadata.get('author', 'Unknown'),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(doc)
            }
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {'title': 'Unknown', 'author': 'Unknown', 'page_count': 0}


if __name__ == "__main__":
    # Test the PDF processor
    processor = PDFProcessor()
    print("PDF Processor initialized successfully!")