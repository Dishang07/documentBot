# 📁 Unified Document QA Bot

A powerful AI-powered document question-answering system that automatically processes different types of documents and provides intelligent responses based on their content.

🌐 **Live Demo**: [https://documentbot.onrender.com/](https://documentbot.onrender.com/)

## ✨ Features

### 🔄 **Automatic Document Routing**
- **Unstructured Documents**: PDF, DOCX, PPTX files are processed using RAG (Retrieval Augmented Generation) with vector embeddings
- **Structured Data**: CSV, XLSX files are processed using intelligent SQL query generation
- Smart file type detection and automatic pipeline selection

### 🧠 **AI-Powered Intelligence**
- **Google Gemini AI** for natural language understanding and response generation
- **Qdrant Vector Database** for semantic search across unstructured documents
- **SQLite** for structured data querying with natural language interface

### 📚 **Multi-Document Knowledge Base**
- Upload multiple documents to build a comprehensive knowledge base
- Automatic duplicate detection prevents redundant processing
- Persistent storage across sessions
- Answer questions from the most recently uploaded document

### 💡 **Smart Query Processing**
- Natural language questions for both structured and unstructured data
- Context-aware responses with source attribution
- Real-time document processing and indexing

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Qdrant Cloud account (or local Qdrant instance)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dishang07/documentBot.git
   cd documentBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   QDRANT_URL=your_qdrant_cluster_url_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 📖 How to Use

### 1. **Upload Documents**
- Simply drag and drop or browse to upload your files
- Supported formats: PDF, DOCX, PPTX, CSV, XLSX
- The system automatically detects the file type and routes it to the appropriate processing pipeline

### 2. **Ask Questions**
- Type your questions in natural language
- For unstructured documents: Ask about content, concepts, or specific information
- For structured data: Ask analytical questions, request summaries, or specific data points

### 3. **Get AI-Powered Answers**
- Receive contextually relevant responses
- Answers are generated specifically from your uploaded documents
- Source attribution shows which document was used

## 🏗️ Architecture

### Unstructured Document Processing
```
PDF/DOCX/PPTX → Document Loader → Text Chunking → Embedding → Qdrant Vector DB → Semantic Search → Gemini AI → Response
```

### Structured Data Processing
```
CSV/XLSX → Pandas → SQLite → Metadata Extraction → Query Routing → SQL Generation → Execution → Gemini AI → Natural Language Response
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Google Gemini AI, Qdrant Vector Database
- **Document Processing**: Unstructured, PyPDF2, python-docx
- **Data Processing**: Pandas, SQLite
- **Deployment**: Render
- **Environment**: Python, dotenv

## 📁 Project Structure

```
unified-project/
├── app.py                         # Main unified application
├── .gitignore                     # Git ignore rules
├── rag-gemini-pdf                 # Unstructured document processing
│   ├── app.py                     # PDF/DOCX/PPTX handler
|   ├── .env                       # Environment variables         
|   ├── requirements.txt           # Dependencies   
│   └── utils/                     # Utility modules
│       ├── document_loader.py     # Document loading and chunking
│       ├── gemini_llm.py          # AI integration
│       └── qdrant_client.py       # Vector database operations
└── rag-structured-data            # Structured data processing
    ├── app.py                     # CSV/XLSX handler
    ├── metadata.py                # Data analysis
    ├── route_query.py             # Query routing
    └── common/                    # Shared utilities
        ├── db.py                  # Database operations
        ├── llm_config.py          # AI configuration
        └── sql_executor.py        # SQL execution
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini AI API key
- `QDRANT_API_KEY`: Your Qdrant vector database API key  
- `QDRANT_URL`: Your Qdrant cluster URL

### Customization Options
- Modify chunk sizes in `document_loader.py`
- Adjust vector similarity thresholds in `qdrant_client.py`
- Customize SQL query templates in `route_query.py`


**Made with ❤️ using Streamlit, Google Gemini AI, and Qdrant**

**Live Demo**: [https://documentbot.onrender.com/](https://documentbot.onrender.com/)
