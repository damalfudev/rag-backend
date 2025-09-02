# Multimodal RAG System - Docker Simulation

**WORKING SYSTEM - DO NOT MODIFY CORE FILES WITHOUT BACKUP**

This is a complete multimodal RAG (Retrieval-Augmented Generation) system that processes scanned PDFs and provides intelligent responses with both text and images.

## 🎯 System Overview

The system processes the 11-page scanned PDF `rag-challenge.pdf` and can answer questions by returning:
- **TEXT ONLY** - When explanation is sufficient
- **IMAGE ONLY** - When diagrams answer the question  
- **BOTH TEXT + IMAGE** - When comprehensive response is needed

## 📁 Directory Structure

```
docker-simulation/
├── main.py                 # FastAPI application (CORE - DO NOT MODIFY)
├── services/
│   ├── __init__.py
│   └── rag_service.py     # RAG logic with OCR (CORE - DO NOT MODIFY)
├── extracted_data/        # Processed content (GENERATED - DO NOT DELETE)
│   ├── text/             # 47 text chunks from OCR
│   ├── images/           # 17 specific diagrams/charts
│   ├── page_images/      # 11 full page images
│   └── tables/           # Table extractions
├── rag-challenge.pdf     # Test document (11 pages, scanned)
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Service orchestration
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── start.sh             # Quick start script
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Start the system
docker-compose up --build

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### Option 2: Direct Python
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### 1. Health Check
```bash
curl -X GET "http://localhost:8000/health/"
```

### 2. Upload PDF
```bash
curl -X POST "http://localhost:8000/upload-pdf/" \
  -F "file=@rag-challenge.pdf"
```

### 3. Query System
```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the AWS architecture?"}'
```

## 🎯 Response Types

### TEXT ONLY Response
**Question:** "What is the main topic of this document?"
```json
{
  "answer": "This document discusses accelerating intelligent document processing with generative AI on AWS...",
  "sources": [
    {"page": 1, "type": "text", "content": "AWS document processing..."}
  ]
}
```

### IMAGE ONLY Response  
**Question:** "Show me the architecture diagram"
```json
{
  "answer": "Here is the AWS architecture diagram:",
  "sources": [
    {"page": 4, "type": "image", "image_file": "specific_image_2.png", "size": 467734}
  ]
}
```

### MULTIMODAL Response (TEXT + IMAGE)
**Question:** "How does the document processing workflow work?"
```json
{
  "answer": "The AWS document processing workflow involves multiple steps...",
  "sources": [
    {"page": 1, "type": "text", "content": "Workflow explanation..."},
    {"page": 8, "type": "image", "image_file": "specific_image_6.png", "size": 232375}
  ]
}
```

## 🔧 Technical Details

### Core Technologies
- **FastAPI** - REST API framework
- **Amazon Bedrock** - Titan embeddings + Nova responses
- **Tesseract OCR** - Text extraction from scanned PDFs
- **FAISS** - Vector similarity search
- **PyMuPDF** - PDF processing and image extraction
- **Docker** - Containerization

### Processing Pipeline
1. **PDF Upload** → OCR text extraction → Text chunking
2. **Image Extraction** → Specific diagrams (not full pages)
3. **Embedding Generation** → Amazon Titan multimodal embeddings
4. **Vector Indexing** → FAISS similarity search
5. **Query Processing** → Retrieve relevant content
6. **Response Generation** → Amazon Nova with context

### Extracted Content Summary
- **47 text chunks** - OCR extracted from all 11 pages
- **17 specific images** - Diagrams, charts, interfaces (not full pages)
- **11 page images** - Full page screenshots for reference
- **Vector index** - 384-dimensional embeddings for similarity search

## ⚠️ IMPORTANT - DO NOT MODIFY

### Critical Files (NEVER CHANGE):
- `main.py` - Core FastAPI application
- `services/rag_service.py` - RAG processing logic
- `extracted_data/` - All processed content

### Safe to Modify:
- `README.md` - This documentation
- `.env` - Environment variables
- `docker-compose.yml` - Container settings (ports, etc.)

## 🐛 Troubleshooting

### Common Issues:
1. **Port 8000 in use**: Change port in docker-compose.yml
2. **AWS credentials**: Ensure ~/.aws/credentials is configured
3. **Memory issues**: Increase Docker memory allocation
4. **OCR errors**: Ensure Tesseract is installed

### Logs:
```bash
# View container logs
docker-compose logs -f

# Check API status
curl http://localhost:8000/health/
```

## 🚀 Deployment to EC2

This system is ready for EC2 deployment:
1. Copy entire `docker-simulation/` folder to EC2
2. Install Docker and docker-compose
3. Configure AWS credentials
4. Run `docker-compose up --build`
5. Configure security groups for port 8000

## 📊 System Status

✅ **FULLY TESTED AND WORKING**
- OCR processing: All 11 pages processed
- Text extraction: 47 chunks generated  
- Image extraction: 17 specific diagrams
- Multimodal responses: Text + Images working
- API endpoints: All functional
- Docker environment: Tested and stable

**Last verified:** September 1, 2024
**Status:** Production ready for EC2 deployment
