import numpy as np
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def search_similar_chunks(query, openai_config, faiss_index, chunks, top_k=3):
    """Search for similar text chunks using FAISS"""
    print(f"🔍 Searching for similar chunks to: '{query[:50]}...'")
    
    try:
        # Create query embedding
        data = {
            "model": "text-embedding-ada-002",
            "input": query.replace("\n", " ").strip()
        }
        
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=openai_config["headers"],
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            query_embedding = result["data"][0]["embedding"]
            query_vector = np.array([query_embedding]).astype('float32')
        else:
            print(f"❌ Query embedding failed: {response.status_code}")
            return []
        
        # Search FAISS index
        distances, indices = faiss_index.search(query_vector, top_k)
        
        print(f"📊 Found {len(indices[0])} similar chunks")
        
        # Get relevant chunks
        relevant_chunks = []
        for i, idx in enumerate(indices[0]):
            if idx < len(chunks):
                chunk_data = {
                    "content": chunks[idx],
                    "score": float(distances[0][i]),
                    "index": int(idx)
                }
                relevant_chunks.append(chunk_data)
                print(f"  📄 Chunk {idx}: score={chunk_data['score']:.4f}")
        
        return relevant_chunks
        
    except Exception as e:
        print(f"❌ Error in similarity search: {str(e)}")
        return []

def find_relevant_images(query, image_mapping, relevant_chunks):
    """Find relevant floorplan images based on query and retrieved chunks"""
    print(f"🖼️ Finding relevant images for query...")
    
    relevant_images = []
    query_lower = query.lower()
    
    # Enhanced villa type detection
    villa_mappings = {
        "shadea": ["4", "5", "6", "7"],  # SHADEA typically on pages 4-7
        "mia": ["2", "3"],              # MIA typically on pages 2-3
        "modea": ["8", "9"],            # MODEA typically on pages 8-9
        "4br": ["4", "5", "6", "7"],
        "4 bedroom": ["4", "5", "6", "7"],
        "3br": ["2", "3"],
        "3 bedroom": ["2", "3"],
        "5br": ["8", "9"],
        "5 bedroom": ["8", "9"]
    }
    
    # Find matching pages based on query
    matching_pages = set()
    for keyword, pages in villa_mappings.items():
        if keyword in query_lower:
            matching_pages.update(pages)
            print(f"  🏠 Detected {keyword} -> pages {pages}")
    
    # Get images for matching pages
    if matching_pages:
        for page_num in sorted(matching_pages):
            if page_num in image_mapping:
                image_info = image_mapping[page_num]
                relevant_images.append({
                    "path": image_info["path"],
                    "description": f"Al Badia Villas floorplan - Page {page_num}",
                    "relevance": "floorplan"
                })
    
    # Fallback: return representative images
    if not relevant_images and image_mapping:
        # Return pages 4, 6 (SHADEA examples) as default
        default_pages = ["4", "6"] if "4" in image_mapping and "6" in image_mapping else list(image_mapping.keys())[:2]
        for page_num in default_pages:
            if page_num in image_mapping:
                img = image_mapping[page_num]
                relevant_images.append({
                    "path": img["path"],
                    "description": f"Al Badia Villas floorplan - {img['filename']}",
                    "relevance": "general"
                })
    
    print(f"✅ Found {len(relevant_images)} relevant images")
    return relevant_images

def generate_rag_response(query, relevant_chunks, relevant_images):
    """Generate response using OpenAI with retrieved context"""
    print("🤖 Generating RAG response with OpenAI...")
    
    # Prepare context from chunks
    context_text = "\n\n".join([chunk["content"] for chunk in relevant_chunks])
    
    system_prompt = """You are a helpful real estate assistant for Al Badia Villas in Dubai Festival City.
    
    CRITICAL RULES:
    - Use ONLY information from the provided context
    - Never invent prices, availability, or features not mentioned
    - Always mention specific villa types (MIA, SHADEA, MODEA) when relevant
    - Include dimensions, areas, and specifications from context
    - For pricing/availability: "Please contact our sales team for current pricing and availability"
    - Be conversational and focus on lead generation
    
    Villa Types:
    - MIA: 3-bedroom villas
    - SHADEA: 4-bedroom villas  
    - MODEA: 5-bedroom villas
    
    Context from Al Badia Villas documentation:
    {context}
    
    Available floorplan images: {image_count} images ready to show
    
    Always mention the specific villa type name (MIA/SHADEA/MODEA) in your response when discussing villa specifications."""
    
    human_prompt = f"User query: {query}\n\nProvide a helpful response about Al Badia Villas."
    
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": system_prompt.format(
                context=context_text[:2000],  # Limit context size
                image_count=len(relevant_images)
            )},
            {"role": "user", "content": human_prompt}
        ]
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OpenAI response generated successfully")
            return result["choices"][0]["message"]["content"]
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            return "I apologize, but I'm having trouble processing your request right now."
        
    except Exception as e:
        print(f"❌ Error generating response: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again."

def extract_citations(relevant_chunks):
    """Extract citation information from retrieved chunks"""
    print("📚 Extracting citations from retrieved chunks...")
    
    citations = []
    for i, chunk in enumerate(relevant_chunks):
        citation = {
            "source": "floorplans_pdf",
            "chunk_index": chunk["index"],
            "relevance_score": chunk["score"],
            "content_preview": chunk["content"][:100] + "..."
        }
        citations.append(citation)
        print(f"  📖 Citation {i+1}: chunk {chunk['index']}")
    
    return citations

def process_rag_query(query, pipeline_data):
    """Main RAG processing function"""
    print(f"\n🎯 Processing RAG query: '{query}'")
    
    # Extract pipeline components
    openai_config = pipeline_data["openai_config"]
    faiss_index = pipeline_data["faiss_index"]
    chunks = pipeline_data["chunks"]
    image_mapping = pipeline_data["image_mapping"]
    
    # Search for relevant chunks
    relevant_chunks = search_similar_chunks(query, openai_config, faiss_index, chunks)
    
    # Find relevant images
    relevant_images = find_relevant_images(query, image_mapping, relevant_chunks)
    
    # Generate response
    response_text = generate_rag_response(query, relevant_chunks, relevant_images)
    
    # Extract citations
    citations = extract_citations(relevant_chunks)
    
    print("✅ RAG query processing completed")
    
    return {
        "response": response_text,
        "relevant_chunks": relevant_chunks,
        "relevant_images": relevant_images,
        "citations": citations
    }

# if __name__ == "__main__":
#     print("🧪 Testing RAG functions...")
#     # This would need pipeline_data from data_ingestion.py
#     print("Note: Run with initialized pipeline data to test fully")
