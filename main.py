from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Import our custom functions
from data_ingestion import initialize_data_pipeline
from rag_functions import process_rag_query
from lead_functions import analyze_lead_potential

# Load environment variables
load_dotenv()
print("🚀 Loading environment variables...")

app = FastAPI(title="Real Estate RAG Chatbot", version="1.0.0")

# Global variable to store pipeline data
pipeline_data = None

@app.on_event("startup")
async def startup_event():
    """Initialize data pipeline on startup"""
    global pipeline_data
    print("🏗️ Initializing RAG pipeline on startup...")
    pipeline_data = initialize_data_pipeline()
    if pipeline_data:
        print("✅ RAG pipeline initialized successfully!")
    else:
        print("❌ Failed to initialize RAG pipeline!")

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    context: Optional[Dict[str, Any]] = {}

class ImageResponse(BaseModel):
    path: str
    description: str
    relevance: str

class LeadSignals(BaseModel):
    intent: str
    signals_detected: List[str]
    recommended_action: str

class ChatResponse(BaseModel):
    response: str
    properties_mentioned: List[str]
    citations: List[Dict[str, Any]]
    images: List[ImageResponse]
    lead_signals: LeadSignals
    follow_up_prompt: str

@app.get("/")
def read_root():
    print("📍 Root endpoint accessed")
    return {"message": "Real Estate RAG Chatbot API", "status": "running"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    print(f"💬 Chat request received: {request.message[:50]}...")
    print(f"🔑 Session ID: {request.session_id}")
    
    if not pipeline_data:
        print("❌ Pipeline not initialized")
        return ChatResponse(
            response="I'm sorry, the system is still initializing. Please try again in a moment.",
            properties_mentioned=[],
            citations=[],
            images=[],
            lead_signals=LeadSignals(
                intent="low",
                signals_detected=[],
                recommended_action="wait"
            ),
            follow_up_prompt="Please try again shortly."
        )
    
    try:
        # Process RAG query
        rag_result = process_rag_query(request.message, pipeline_data)
        
        # Analyze lead potential
        lead_analysis = analyze_lead_potential(request.message, request.context)
        
        # Extract properties mentioned - improved detection
        properties_mentioned = []
        message_lower = request.message.lower()
        response_lower = rag_result["response"].lower()
        
        # Check both message and response for property mentions
        combined_text = message_lower + " " + response_lower
        
        if any(word in combined_text for word in ["shadea", "4br", "4 bedroom", "four bedroom", "4-bedroom"]):
            properties_mentioned.append("SHADEA-4BR")
        if any(word in combined_text for word in ["mia", "3br", "3 bedroom", "three bedroom", "3-bedroom"]):
            properties_mentioned.append("MIA-3BR")
        if any(word in combined_text for word in ["modea", "5br", "5 bedroom", "five bedroom", "5-bedroom"]):
            properties_mentioned.append("MODEA-5BR")
        
        # Convert images to response format
        images = []
        for img in rag_result["relevant_images"]:
            images.append(ImageResponse(
                path=img["path"],
                description=img["description"],
                relevance=img["relevance"]
            ))
        
        response = ChatResponse(
            response=rag_result["response"],
            properties_mentioned=properties_mentioned,
            citations=rag_result["citations"],
            images=images,
            lead_signals=LeadSignals(
                intent=lead_analysis["intent"],
                signals_detected=lead_analysis["signals_detected"],
                recommended_action=lead_analysis["recommended_action"]
            ),
            follow_up_prompt=lead_analysis["follow_up_prompt"]
        )
        
        print("✅ Response generated successfully")
        return response
        
    except Exception as e:
        print(f"❌ Error processing chat request: {str(e)}")
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request. Please try again.",
            properties_mentioned=[],
            citations=[],
            images=[],
            lead_signals=LeadSignals(
                intent="low",
                signals_detected=[],
                recommended_action="retry"
            ),
            follow_up_prompt="How else can I help you with Al Badia Villas?"
        )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pipeline_initialized": pipeline_data is not None
    }

if __name__ == "__main__":
    import uvicorn
    print("🏠 Starting Real Estate RAG Chatbot...")
    uvicorn.run(app, host="0.0.0.0", port=8000)