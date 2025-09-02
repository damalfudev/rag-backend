"""
Multimodal RAG API - FastAPI Application
WORKING SYSTEM - DO NOT MODIFY WITHOUT BACKUP

This API provides multimodal RAG functionality for scanned PDFs.
Returns TEXT, IMAGE, or BOTH based on query context.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from services.rag_service import RAGService

# Initialize FastAPI app
app = FastAPI(
    title="Multimodal RAG API", 
    version="1.0.0",
    description="Processes scanned PDFs and provides intelligent multimodal responses"
)

# CORS middleware - allows frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service - CORE COMPONENT
rag_service = RAGService()

# Request/Response models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list

# API Endpoints
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process PDF file with OCR
    Returns: Processing confirmation with item count
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process the PDF - CORE FUNCTIONALITY
        result = await rag_service.process_pdf(file_path)
        return {"message": "PDF processed successfully", "items_processed": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/query/", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system - Returns TEXT, IMAGE, or BOTH
    Input: Question string
    Output: Multimodal response with sources
    """
    try:
        # Core RAG query processing
        response = await rag_service.query(request.question)
        return QueryResponse(answer=response["answer"], sources=response["sources"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "system": "multimodal-rag", "version": "1.0.0"}

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
