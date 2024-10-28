from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import jwt
import motor.motor_asyncio
from datetime import datetime, timedelta

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

# Initialize MongoDB client
MONGODB_URL = os.getenv("MONGODB_URL")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = mongo_client.parenting_assistant

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

class WeChatLoginRequest(BaseModel):
    code: str
    user_info: dict

# Authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user_id
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# Login endpoint
@app.post("/api/login")
async def login(request: WeChatLoginRequest):
    try:
        # Here you would typically verify the WeChat code with WeChat's API
        # For now, we'll just create a user record
        user = {
            "wechat_info": request.user_info,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user)
        user_id = str(result.inserted_id)
        
        # Create JWT token
        token = jwt.encode(
            {
                "sub": user_id,
                "exp": datetime.utcnow() + timedelta(days=30)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create thread endpoint
@app.post("/api/thread")
async def create_thread(current_user: str = Depends(get_current_user)):
    try:
        thread = client.beta.threads.create()
        
        # Store thread info in database
        await db.threads.insert_one({
            "thread_id": thread.id,
            "user_id": current_user,
            "created_at": datetime.utcnow()
        })
        
        return {"thread_id": thread.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest, current_user: str = Depends(get_current_user)):
    try:
        # Validate OpenAI configuration
        if not os.getenv("OPENAI_API_KEY") or not ASSISTANT_ID:
            raise HTTPException(status_code=500, detail="OpenAI configuration missing")

        # Verify thread ownership
        thread = await db.threads.find_one({
            "thread_id": request.thread_id,
            "user_id": current_user
        })
        if not thread:
            raise HTTPException(status_code=403, detail="Thread not found or access denied")

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

        # Store message in database
        await db.messages.insert_one({
            "thread_id": request.thread_id,
            "user_id": current_user,
            "message": request.message,
            "user_info": request.user_info.dict(),
            "question_type": request.question_type,
            "subcategory": request.subcategory,
            "created_at": datetime.utcnow()
        })

        # Add message to thread
        message = client.beta.threads.messages.create(
            thread_id=request.thread_id,
            role="user",
            content=user_info_str
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=request.thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for completion with timeout
        start_time = time.time()
        timeout = 30  # 30 seconds timeout
        
        while run.status not in ["completed", "failed"]:
            if time.time() - start_time > timeout:
                raise HTTPException(status_code=504, detail="Request timeout")
            
            run = client.beta.threads.runs.retrieve(
                thread_id=request.thread_id,
                run_id=run.id
            )
            
            if run.status == "failed":
                raise HTTPException(status_code=500, detail="Assistant failed to respond")
            
            time.sleep(0.5)

        # Get the latest message
        messages = client.beta.threads.messages.list(thread_id=request.thread_id)
        if not messages.data:
            raise HTTPException(status_code=500, detail="No response generated")

        response_message = messages.data[0].content[0].text.value

        # Store AI response in database
        await db.responses.insert_one({
            "thread_id": request.thread_id,
            "user_id": current_user,
            "message": response_message,
            "created_at": datetime.utcnow()
        })

        return {
            "message": response_message,
            "thread_id": request.thread_id
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

# Clear chat endpoint
@app.post("/api/clear")
async def clear_chat(thread_id: str, current_user: str = Depends(get_current_user)):
    try:
        # Verify thread ownership
        thread = await db.threads.find_one({
            "thread_id": thread_id,
            "user_id": current_user
        })
        if not thread:
            raise HTTPException(status_code=403, detail="Thread not found or access denied")

        # Create new thread
        new_thread = client.beta.threads.create()
        
        # Store new thread info
        await db.threads.insert_one({
            "thread_id": new_thread.id,
            "user_id": current_user,
            "created_at": datetime.utcnow()
        })
        
        return {"thread_id": new_thread.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=30)
