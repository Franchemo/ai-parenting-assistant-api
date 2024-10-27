from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Parenting Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Models
class UserInfo(BaseModel):
    childAge: str
    childPersonality: str
    kindergarten: str
    interests: str
    languages: str
    familyMembers: int
    hasSiblings: str
    siblingsAge: Optional[str] = None

class ChatRequest(BaseModel):
    thread_id: Optional[str]
    message: str
    user_info: UserInfo
    question_type: str
    subcategory: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "AI Parenting Assistant API is running",
        "timestamp": time.time()
    }

# OpenAI connection test
@app.get("/api/health")
async def health_check():
    try:
        # Test OpenAI connection
        client.models.list(limit=1)
        return {
            "status": "healthy",
            "openai_connection": "connected",
            "assistant_id": ASSISTANT_ID is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI connection failed: {str(e)}")

@app.post("/api/thread")
async def create_thread():
    """Create a new chat thread"""
    try:
        thread = client.beta.threads.create()
        return {"thread_id": thread.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Process chat messages and return AI responses"""
    try:
        # Validate OpenAI configuration
        if not os.getenv("OPENAI_API_KEY") or not ASSISTANT_ID:
            raise HTTPException(status_code=500, detail="OpenAI configuration missing")

        # Create thread if not provided
        thread_id = request.thread_id
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id

        # Format user information
        user_info_str = f"""
User Information:
Child's Age: {request.user_info.childAge}
Personality Traits: {request.user_info.childPersonality}
In Kindergarten: {request.user_info.kindergarten}
Interests: {request.user_info.interests}
Languages at Home: {request.user_info.languages}
Family Members: {request.user_info.familyMembers}
Has Siblings: {request.user_info.hasSiblings}
{f"Siblings' Ages: {request.user_info.siblingsAge}" if request.user_info.siblingsAge else ""}

Question Type: {request.question_type}
{f"Specific Topic: {request.subcategory}" if request.subcategory else ""}
Question: {request.message}
"""

        # Add message to thread
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_info_str
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for completion with timeout
        start_time = time.time()
        timeout = 30  # 30 seconds timeout
        
        while run.status not in ["completed", "failed"]:
            if time.time() - start_time > timeout:
                raise HTTPException(status_code=504, detail="Request timeout - Assistant took too long to respond")
            
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if run.status == "failed":
                raise HTTPException(status_code=500, detail="Assistant failed to generate response")
            
            # Small delay to prevent too frequent API calls
            time.sleep(0.5)

        # Get the latest message
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        if not messages.data:
            raise HTTPException(status_code=500, detail="No response generated")

        return {
            "message": messages.data[0].content[0].text.value,
            "thread_id": thread_id
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear")
async def clear_chat(thread_id: str):
    """Clear chat history by creating a new thread"""
    try:
        new_thread = client.beta.threads.create()
        return {"thread_id": new_thread.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Startup event
@app.on_event("startup")
async def startup_event():
    # Validate required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    if not ASSISTANT_ID:
        raise RuntimeError("OPENAI_ASSISTANT_ID environment variable is not set")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=30)