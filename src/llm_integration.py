"""
LLM Integration Module for StudyMate
Integrates IBM Watson's Mixtral-8x7B-Instruct model for answer generation
"""

import os
import requests
import json
from typing import List, Dict, Optional
import logging
from datetime import datetime

# For fallback when IBM Watson is not available
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAnswerGenerator:
    """Generates answers using LLM models with retrieved context"""
    
    def __init__(self, use_watson: bool = True):
        """
        Initialize the answer generator
        
        Args:
            use_watson (bool): Whether to use IBM Watson or fallback model
        """
        self.use_watson = use_watson
        self.watson_api_key = os.getenv('WATSON_API_KEY')
        self.watson_url = os.getenv('WATSON_URL')
        self.project_id = os.getenv('WATSON_PROJECT_ID')
        
        # Fallback model setup
        self.fallback_model = None
        self.fallback_tokenizer = None
        
        if not self.use_watson or not all([self.watson_api_key, self.watson_url, self.project_id]):
            logger.warning("IBM Watson credentials not found, will use fallback model")
            self.use_watson = False
            self._setup_fallback_model()
    
    def _setup_fallback_model(self):
        """Setup fallback model when Watson is not available"""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Transformers library not available for fallback model")
            return
        
        try:
            # Use a smaller model as fallback
            model_name = "microsoft/DialoGPT-medium"
            logger.info(f"Loading fallback model: {model_name}")
            
            self.fallback_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.fallback_model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token if not present
            if self.fallback_tokenizer.pad_token is None:
                self.fallback_tokenizer.pad_token = self.fallback_tokenizer.eos_token
            
            logger.info("Fallback model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading fallback model: {str(e)}")
    
    def _call_watson_api(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """
        Call IBM Watson Machine Learning API
        
        Args:
            prompt (str): Input prompt
            max_tokens (int): Maximum tokens to generate
            temperature (float): Sampling temperature
            
        Returns:
            Optional[str]: Generated response
        """
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.watson_api_key}'
            }
            
            payload = {
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "stop_sequences": ["Human:", "Assistant:", "\n\n"]
                },
                "model_id": "mistralai/mixtral-8x7b-instruct-v01",
                "project_id": self.project_id
            }
            
            response = requests.post(
                f"{self.watson_url}/ml/v1-beta/generation/text",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('results', [{}])[0].get('generated_text', '').strip()
            else:
                logger.error(f"Watson API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Watson API: {str(e)}")
            return None
    
    def _generate_with_fallback(self, prompt: str, max_tokens: int = 512) -> Optional[str]:
        """
        Generate response using fallback model
        
        Args:
            prompt (str): Input prompt
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            Optional[str]: Generated response
        """
        if not self.fallback_model or not self.fallback_tokenizer:
            return "I apologize, but the AI model is currently unavailable. Please try again later."
        
        try:
            # Encode input
            inputs = self.fallback_tokenizer.encode(prompt, return_tensors='pt', truncate=True, max_length=512)
            
            # Generate response
            with torch.no_grad():
                outputs = self.fallback_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + min(max_tokens, 200),
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.fallback_tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.fallback_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part
            generated_text = response[len(prompt):].strip()
            
            return generated_text if generated_text else "I need more context to provide a helpful answer."
            
        except Exception as e:
            logger.error(f"Error with fallback model: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def create_context_prompt(self, question: str, context_chunks: List[Dict[str, any]], 
                            document_title: str = "Document") -> str:
        """
        Create a well-formatted prompt with context and question
        
        Args:
            question (str): User's question
            context_chunks (List[Dict]): Retrieved relevant chunks
            document_title (str): Title of the source document
            
        Returns:
            str: Formatted prompt
        """
        # Combine context chunks
        context_text = ""
        for i, chunk in enumerate(context_chunks[:5], 1):  # Limit to top 5 chunks
            context_text += f"[Context {i}]\n{chunk['text']}\n\n"
        
        prompt = f"""You are StudyMate, an AI academic assistant that helps students understand their study materials. You have been provided with relevant excerpts from "{document_title}" to answer the student's question.

Context from the document:
{context_text}

Student's Question: {question}

Instructions:
- Provide a clear, accurate answer based on the provided context
- Reference specific information from the context when relevant
- If the context doesn't contain enough information, say so honestly
- Use an educational tone that helps the student learn
- Keep your answer concise but comprehensive

Answer:"""
        
        return prompt
    
    def generate_answer(self, question: str, context_chunks: List[Dict[str, any]], 
                       document_title: str = "Document") -> Dict[str, any]:
        """
        Generate an answer based on the question and retrieved context
        
        Args:
            question (str): User's question
            context_chunks (List[Dict]): Retrieved relevant chunks
            document_title (str): Title of the source document
            
        Returns:
            Dict: Answer with metadata
        """
        try:
            # Create prompt
            prompt = self.create_context_prompt(question, context_chunks, document_title)
            
            # Generate answer
            if self.use_watson:
                answer = self._call_watson_api(prompt)
            else:
                answer = self._generate_with_fallback(prompt)
            
            if not answer:
                answer = "I apologize, but I'm unable to generate an answer at this time. Please try rephrasing your question or check your connection."
            
            # Prepare response
            response = {
                'answer': answer,
                'question': question,
                'document_title': document_title,
                'context_chunks_used': len(context_chunks),
                'model_used': 'IBM Watson Mixtral-8x7B' if self.use_watson else 'Fallback Model',
                'timestamp': datetime.now().isoformat(),
                'sources': []
            }
            
            # Add source information
            for chunk in context_chunks[:3]:  # Top 3 sources
                response['sources'].append({
                    'chunk_id': chunk.get('id', 'unknown'),
                    'similarity_score': chunk.get('similarity_score', 0.0),
                    'text_preview': chunk['text'][:100] + '...' if len(chunk['text']) > 100 else chunk['text']
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                'answer': "I encountered an error while generating the answer. Please try again.",
                'question': question,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_follow_up_questions(self, question: str, answer: str, 
                                   context_chunks: List[Dict[str, any]]) -> List[str]:
        """
        Generate follow-up questions based on the current Q&A
        
        Args:
            question (str): Original question
            answer (str): Generated answer
            context_chunks (List[Dict]): Context used
            
        Returns:
            List[str]: List of follow-up questions
        """
        try:
            prompt = f"""Based on this Q&A interaction, generate 3 relevant follow-up questions that a student might ask to deepen their understanding:

Original Question: {question}
Answer: {answer}

Generate 3 follow-up questions that would help the student learn more about this topic:
1."""
            
            if self.use_watson:
                response = self._call_watson_api(prompt, max_tokens=150)
            else:
                response = self._generate_with_fallback(prompt, max_tokens=150)
            
            if response:
                # Parse the response to extract questions
                lines = response.split('\n')
                questions = []
                
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith(('1.', '2.', '3.')) or line.startswith('-')):
                        # Clean up the question
                        question = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ')
                        if question and len(question) > 10:
                            questions.append(question)
                
                return questions[:3]
            
            # Fallback questions if generation fails
            return [
                "Can you explain this concept in more detail?",
                "What are some related topics I should study?",
                "Can you provide an example to illustrate this?"
            ]
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {str(e)}")
            return []
    
    def summarize_document_section(self, chunks: List[Dict[str, any]], 
                                 section_title: str = "Document Section") -> str:
        """
        Generate a summary of document chunks
        
        Args:
            chunks (List[Dict]): Document chunks to summarize
            section_title (str): Title for the section
            
        Returns:
            str: Generated summary
        """
        try:
            # Combine chunks
            text = " ".join([chunk['text'] for chunk in chunks])
            
            prompt = f"""Please provide a concise summary of the following text from "{section_title}":

{text[:2000]}  # Limit text length

Summary:"""
            
            if self.use_watson:
                summary = self._call_watson_api(prompt, max_tokens=200)
            else:
                summary = self._generate_with_fallback(prompt, max_tokens=200)
            
            return summary or "Unable to generate summary at this time."
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Error generating summary."


if __name__ == "__main__":
    # Test the LLM integration
    generator = LLMAnswerGenerator(use_watson=False)  # Use fallback for testing
    print("LLM Answer Generator initialized successfully!")
    print(f"Using Watson: {generator.use_watson}")
    
    # Test with sample context
    sample_chunks = [
        {'id': 0, 'text': 'Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.', 'similarity_score': 0.9},
        {'id': 1, 'text': 'Deep learning uses neural networks with multiple layers to process complex patterns in data.', 'similarity_score': 0.8}
    ]
    
    result = generator.generate_answer(
        "What is machine learning?", 
        sample_chunks, 
        "AI Textbook"
    )
    
    print(f"Sample answer: {result['answer'][:100]}...")