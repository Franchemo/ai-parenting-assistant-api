from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

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

# API Endpoints
@app.get("/")
async def root():
    return {"message": "AI Parenting Assistant API is running"}

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
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_info_str
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for completion
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run.status == "failed":
                raise HTTPException(status_code=500, detail="Assistant failed to generate response")

        # Get the latest message
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        if not messages.data:
            raise HTTPException(status_code=500, detail="No response generated")

        return {"message": messages.data[0].content[0].text.value}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear")
async def clear_chat(thread_id: str):
    """Clear chat history by creating a new thread"""
    try:
        new_thread = client.beta.threads.create()
        return {"thread_id": new_thread.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
