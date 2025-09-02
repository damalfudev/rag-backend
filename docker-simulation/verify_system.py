#!/usr/bin/env python3
"""
System Verification Script
Run this to verify the RAG system is working after any changes
"""

import os
import sys

def verify_files():
    """Verify all critical files exist"""
    critical_files = [
        "main.py",
        "services/rag_service.py", 
        "services/__init__.py",
        "rag-challenge.pdf",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    print("🔍 Verifying critical files...")
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            return False
    return True

def verify_extracted_data():
    """Verify processed data exists"""
    print("\n📊 Verifying extracted data...")
    
    if not os.path.exists("extracted_data"):
        print("❌ extracted_data folder missing!")
        return False
    
    text_count = len(os.listdir("extracted_data/text")) if os.path.exists("extracted_data/text") else 0
    image_count = len([f for f in os.listdir("extracted_data/images") if f.endswith('.png')]) if os.path.exists("extracted_data/images") else 0
    page_count = len(os.listdir("extracted_data/page_images")) if os.path.exists("extracted_data/page_images") else 0
    
    print(f"📝 Text chunks: {text_count}")
    print(f"🖼️ Specific images: {image_count}")
    print(f"📄 Page images: {page_count}")
    
    if text_count >= 40 and image_count >= 15 and page_count >= 10:
        print("✅ Extracted data looks good")
        return True
    else:
        print("⚠️ Extracted data seems incomplete")
        return False

def verify_imports():
    """Verify Python imports work"""
    print("\n🐍 Verifying Python imports...")
    
    try:
        from services.rag_service import RAGService
        print("✅ RAGService import")
        
        from fastapi import FastAPI
        print("✅ FastAPI import")
        
        import boto3
        print("✅ boto3 import")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("🚀 MULTIMODAL RAG SYSTEM VERIFICATION")
    print("=" * 50)
    
    checks = [
        verify_files(),
        verify_extracted_data(), 
        verify_imports()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("✅ SYSTEM VERIFICATION PASSED")
        print("🎯 RAG system is ready to use!")
        return 0
    else:
        print("❌ SYSTEM VERIFICATION FAILED")
        print("⚠️ Check the issues above before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())
