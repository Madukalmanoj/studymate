# 📚 StudyMate - AI-Powered PDF-Based Q&A System

StudyMate is an AI-powered academic assistant that enables students to interact with their study materials—such as textbooks, lecture notes, and research papers—in a conversational, question-answering format. Instead of passively reading large PDF documents or relying on manual searches for specific information, users can simply upload one or more PDFs and ask natural-language questions. StudyMate responds with direct, well-contextualized answers, referenced from the source content.

## 🌟 Key Features

### 1. Conversational Q&A from Academic PDFs
- Upload PDF documents (textbooks, research papers, lecture notes)
- Ask natural-language questions about the content
- Get contextual answers grounded in the uploaded material

### 2. Accurate Text Extraction and Preprocessing
- Efficiently extracts and chunks content from multiple PDFs using PyMuPDF
- High-quality downstream processing for optimal search results

### 3. Semantic Search Using FAISS and Embeddings
- Retrieves the most relevant text chunks using SentenceTransformers and FAISS
- Precise question matching with semantic understanding

### 4. LLM-Based Answer Generation
- Uses IBM Watson's Mixtral-8x7B-Instruct model for informative, grounded answers
- Fallback to local models when Watson is unavailable

### 5. User-Friendly Local Interface
- Intuitive Streamlit-based frontend for seamless document upload
- Clean interface for question input and result visualization
- Conversation history and document management

## 🛠️ Technology Stack

- **Python 3.8+**
- **Streamlit** - Web interface
- **IBM Watson** - LLM for answer generation
- **Hugging Face** - SentenceTransformers for embeddings
- **PyMuPDF** - PDF text extraction
- **Mistral** - Mixtral-8x7B-Instruct model
- **FAISS** - Vector similarity search

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd studymate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables (optional for IBM Watson):**
```bash
cp .env.example .env
# Edit .env with your IBM Watson credentials
```

4. **Run the application:**
```bash
python run_app.py
```

The application will start on `http://localhost:8501`

### Alternative: Direct Streamlit Launch
```bash
streamlit run app.py
```

## 📖 Usage Guide

### 1. Upload Documents
- Click "Upload PDF Document" in the sidebar
- Select your PDF file (textbooks, papers, notes)
- Wait for processing to complete

### 2. Ask Questions
- Type your question in the text area
- Click "Ask Question" to get AI-generated answers
- View sources and follow-up questions

### 3. Explore Features
- **Document Summary**: Get an overview of uploaded documents
- **Search**: Find specific passages without generating answers
- **Conversation History**: Review previous Q&A sessions
- **Multiple Documents**: Upload and switch between different PDFs

## 🔧 Configuration

### IBM Watson Setup (Recommended)
To use IBM Watson's Mixtral-8x7B model:

1. Create an IBM Cloud account
2. Set up Watson Machine Learning service
3. Get your API key and project ID
4. Configure in `.env` file:

```env
WATSON_API_KEY=your_api_key
WATSON_URL=https://us-south.ml.cloud.ibm.com
WATSON_PROJECT_ID=your_project_id
```

### Fallback Mode
Without Watson credentials, the system automatically uses a fallback model for basic functionality.

## 📁 Project Structure

```
studymate/
├── src/                    # Core application modules
│   ├── pdf_processor.py    # PDF text extraction
│   ├── semantic_search.py  # FAISS-based search
│   ├── llm_integration.py  # LLM answer generation
│   └── qa_system.py        # Main orchestration
├── data/                   # Document storage and indices
├── uploads/                # Temporary file uploads
├── models/                 # Model cache
├── app.py                  # Streamlit frontend
├── run_app.py             # Application launcher
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🧪 Testing

The system includes built-in testing capabilities:

1. **Upload a sample PDF** (research paper, textbook chapter)
2. **Ask questions** like:
   - "What is the main topic of this document?"
   - "Can you summarize the key findings?"
   - "Explain the methodology used"
3. **Verify responses** are grounded in the source material

## 🔍 Features in Detail

### PDF Processing
- Extracts text from complex academic PDFs
- Handles multi-column layouts and figures
- Chunks text for optimal semantic search
- Preserves document metadata

### Semantic Search
- Uses state-of-the-art sentence embeddings
- FAISS indexing for fast similarity search
- Contextual chunk retrieval
- Relevance scoring and ranking

### Answer Generation
- Context-aware response generation
- Source attribution and references
- Follow-up question suggestions
- Conversation memory

### User Interface
- Clean, intuitive design
- Real-time processing feedback
- Document management
- Conversation history
- Mobile-responsive layout

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or contributions:

1. Check the documentation
2. Search existing issues
3. Create a new issue with details
4. Provide sample PDFs and questions for debugging

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Batch document processing
- [ ] Advanced citation formatting
- [ ] Integration with academic databases
- [ ] Mobile app version
- [ ] Collaborative study features

---

**StudyMate** - Making academic research and study more interactive and efficient! 📚✨
