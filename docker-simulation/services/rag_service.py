import boto3
import json
import base64
import os
import numpy as np
import faiss
import pymupdf
import tabula
import pytesseract
from pdf2image import convert_from_path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import ChatBedrock
from botocore.exceptions import ClientError
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.embedding_dimension = 384
        self.index = None
        self.items = []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700, chunk_overlap=200, length_function=len
        )
        
    async def process_pdf(self, file_path: str):
        """Process PDF file with OCR for scanned documents"""
        self.items = []
        base_dir = "data"
        self._create_directories(base_dir)
        
        # Convert PDF to images for OCR processing
        images = convert_from_path(file_path)
        
        for page_num, image in enumerate(tqdm(images, desc="Processing PDF pages with OCR")):
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            # Process text chunks
            if text.strip():
                self._process_text_chunks(text, page_num, base_dir)
            
            # Save page image
            page_path = f"{base_dir}/page_images/page_{page_num:03d}.png"
            image.save(page_path)
            with open(page_path, "rb") as f:
                page_image = base64.b64encode(f.read()).decode("utf8")
            self.items.append({
                "page": page_num,
                "type": "page",
                "path": page_path,
                "image": page_image,
            })
        
        # Generate embeddings
        await self._generate_embeddings()
        self._create_vector_index()
        
        return len(self.items)
    
    def _create_directories(self, base_dir: str):
        """Create necessary directories"""
        directories = ["images", "text", "tables", "page_images"]
        for dir_name in directories:
            os.makedirs(os.path.join(base_dir, dir_name), exist_ok=True)
    
    def _process_text_chunks(self, text: str, page_num: int, base_dir: str):
        """Process text into chunks"""
        chunks = self.text_splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            text_file_name = f"{base_dir}/text/text_{page_num}_{i}.txt"
            with open(text_file_name, "w") as f:
                f.write(chunk)
            self.items.append({
                "page": page_num,
                "type": "text",
                "text": chunk,
                "path": text_file_name,
            })
    
    async def _generate_embeddings(self):
        """Generate embeddings for all items"""
        for item in tqdm(self.items, desc="Generating embeddings"):
            if item["type"] == "text":
                item["embedding"] = self._generate_multimodal_embeddings(prompt=item["text"])
            else:
                item["embedding"] = self._generate_multimodal_embeddings(image=item["image"])
    
    def _generate_multimodal_embeddings(self, prompt=None, image=None):
        """Generate embeddings using Amazon Titan"""
        client = boto3.client(service_name="bedrock-runtime")
        model_id = "amazon.titan-embed-image-v1"
        
        body = {"embeddingConfig": {"outputEmbeddingLength": self.embedding_dimension}}
        
        if prompt:
            body["inputText"] = prompt
        if image:
            body["inputImage"] = image
        
        try:
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                accept="application/json",
                contentType="application/json",
            )
            result = json.loads(response.get("body").read())
            return result.get("embedding")
        except ClientError as err:
            logger.error(f"Bedrock error: {err}")
            return None
    
    def _create_vector_index(self):
        """Create FAISS vector index"""
        all_embeddings = np.array([item["embedding"] for item in self.items if item.get("embedding")])
        if len(all_embeddings) == 0:
            return
        
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        self.index.add(np.array(all_embeddings, dtype=np.float32))
    
    async def query(self, question: str):
        """Query the RAG system"""
        if not self.index:
            raise ValueError("No processed documents available")
        
        query_embedding = self._generate_multimodal_embeddings(prompt=question)
        distances, indices = self.index.search(
            np.array(query_embedding, dtype=np.float32).reshape(1, -1), k=5
        )
        
        matched_items = [
            {k: v for k, v in self.items[idx].items() if k != "embedding"}
            for idx in indices.flatten()
        ]
        
        response = self._invoke_nova_multimodal(question, matched_items)
        
        return {
            "answer": response,
            "sources": [{"page": item["page"], "type": item["type"]} for item in matched_items]
        }
    
    def _invoke_nova_multimodal(self, prompt: str, matched_items: list):
        """Generate response using Amazon Nova"""
        system_msg = [{"text": "You are a helpful assistant. Use the provided text and images to answer questions."}]
        
        message_content = []
        for item in matched_items:
            if item["type"] == "text":
                message_content.append({"text": item["text"]})
            else:
                message_content.append({
                    "image": {
                        "format": "png",
                        "source": {"bytes": item["image"]},
                    }
                })
        
        message_list = [
            {"role": "user", "content": message_content},
            {"role": "user", "content": [{"text": prompt}]}
        ]
        
        native_request = {
            "messages": message_list,
            "system": system_msg,
            "inferenceConfig": {"max_new_tokens": 300, "top_p": 0.9, "top_k": 20}
        }
        
        try:
            client = ChatBedrock(model_id="amazon.nova-pro-v1:0")
            response = client.invoke(json.dumps(native_request))
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"
