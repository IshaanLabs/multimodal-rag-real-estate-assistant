import os
import pymupdf4llm
import faiss
import numpy as np
import requests
import json
from dotenv import load_dotenv
import re

load_dotenv()

def load_pdf_with_pymupdf(pdf_path):
    """Load and extract text from PDF using pymupdf4llm"""
    print(f"📄 Loading PDF from: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return None
    
    try:
        print("🔄 Converting PDF with pymupdf4llm...")
        text_content = pymupdf4llm.to_markdown(pdf_path)
        
        print(f"✅ PDF loaded successfully. Content length: {len(text_content)} characters")
        return text_content
        
    except Exception as e:
        print(f"❌ Error loading PDF: {str(e)}")
        return None

def chunk_text(text_content, chunk_size=800, chunk_overlap=100):
    """Split text into chunks optimized for villa specifications"""
    print(f"✂️ Chunking text with size: {chunk_size}, overlap: {chunk_overlap}")
    
    # Clean and preprocess text
    cleaned_text = text_content.replace('\n\n', '\n').replace('\t', ' ')
    
    # Split by sections first (villa types, specifications)
    sections = []
    
    # Look for villa type sections (MIA, SHADEA, MODEA)
    villa_keywords = ['MIA', 'SHADEA', 'MODEA', 'bedroom', 'villa', 'specifications', 'dimensions', 'area']
    
    # Split into paragraphs first
    paragraphs = cleaned_text.split('\n')
    current_section = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Check if paragraph contains villa-specific info
        if any(keyword.lower() in para.lower() for keyword in villa_keywords):
            if current_section and len(current_section) > 100:
                sections.append(current_section.strip())
                current_section = para
            else:
                current_section += " " + para
        else:
            current_section += " " + para
        
        # If section gets too long, split it
        if len(current_section) > chunk_size:
            sections.append(current_section.strip())
            current_section = ""
    
    # Add remaining section
    if current_section.strip():
        sections.append(current_section.strip())
    
    # If no good sections found, fall back to simple chunking
    if not sections or len(sections) < 3:
        print("⚠️ Falling back to simple chunking")
        chunks = []
        start = 0
        while start < len(cleaned_text):
            end = start + chunk_size
            chunk = cleaned_text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
            if start >= len(cleaned_text):
                break
        sections = chunks
    
    print(f"✅ Created {len(sections)} optimized chunks")
    return sections

def create_embeddings(chunks):
    """Create embeddings for text chunks using OpenAI text-embedding-ada-002"""
    print("🧠 Creating embeddings with OpenAI text-embedding-ada-002...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found")
        return None, None
    
    try:
        embeddings = []
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        for i, chunk in enumerate(chunks):
            print(f"  📄 Processing chunk {i+1}/{len(chunks)}")
            
            data = {
                "model": "text-embedding-ada-002",
                "input": chunk.replace("\n", " ").strip()
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                embeddings.append(result["data"][0]["embedding"])
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return None, None
        
        print(f"✅ Created embeddings for {len(embeddings)} chunks")
        return embeddings, {"api_key": api_key, "headers": headers}
        
    except Exception as e:
        print(f"❌ Error creating embeddings: {str(e)}")
        return None, None

def create_faiss_index(embeddings):
    """Create FAISS vector index"""
    print("🗂️ Creating FAISS vector index...")
    
    if not embeddings:
        print("❌ No embeddings provided")
        return None
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings).astype('float32')
    dimension = embeddings_array.shape[1]
    
    print(f"📊 Embedding dimension: {dimension}")
    
    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    print(f"✅ FAISS index created with {index.ntotal} vectors")
    return index

def map_images_to_villas():
    """Create mapping between villa types and floorplan images"""
    print("🖼️ Creating image-to-villa mapping...")
    
    image_dir = "data/WebP"
    image_mapping = {}
    
    # Villa type patterns based on the requirements
    villa_patterns = {
        "3BR": ["MIA", "Type A", "Type B"],
        "4BR": ["SHADEA", "Type A", "Type B"], 
        "5BR": ["MODEA", "Type A", "Type B"]
    }
    
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            if filename.startswith("AlBadia_Floorplans_A3_Rev11") and filename.endswith(".webp"):
                print(f"📸 Found image: {filename}")
                
                # Extract page number from filename (e.g., Rev11-7.webp -> page 7)
                page_num = filename.split("-")[-1].split(".")[0]
                image_path = os.path.join(image_dir, filename)
                
                image_mapping[page_num] = {
                    "path": image_path,
                    "filename": filename,
                    "villa_type": f"Page_{page_num}"  # Will be refined based on PDF content
                }
    
    print(f"✅ Created mapping for {len(image_mapping)} images")
    return image_mapping

def initialize_data_pipeline():
    """Initialize the complete data ingestion pipeline"""
    print("🏗️ Initializing data ingestion pipeline...")
    
    # Load PDF
    pdf_path = "data/ABV Final Floorplans.pdf"
    text_content = load_pdf_with_pymupdf(pdf_path)
    
    if not text_content:
        print("❌ Failed to load PDF content")
        return None
    
    # Create chunks
    chunks = chunk_text(text_content)
    
    # Create embeddings
    embeddings, openai_config = create_embeddings(chunks)
    
    if not embeddings:
        print("❌ Failed to create embeddings")
        return None
    
    # Create FAISS index
    faiss_index = create_faiss_index(embeddings)
    
    # Create image mapping
    image_mapping = map_images_to_villas()
    
    pipeline_data = {
        "chunks": chunks,
        "openai_config": openai_config,
        "faiss_index": faiss_index,
        "image_mapping": image_mapping,
        "text_content": text_content
    }
    
    print("✅ Data pipeline initialized successfully!")
    return pipeline_data

if __name__ == "__main__":
    print("🚀 Testing data ingestion pipeline...")
    result = initialize_data_pipeline()
    if result:
        print("🎉 Pipeline test completed successfully!")
    else:
        print("💥 Pipeline test failed!")
