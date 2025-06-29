from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from ai_email_agent import AIEmailAgent, create_ai_demo_screenshots
from typing import Dict, List
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Email Agent v2", description="Intelligent Gmail automation with AI-powered content generation")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for screenshots
os.makedirs("screenshots", exist_ok=True)
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

class AIEmailRequest(BaseModel):
    gmail_id: str
    gmail_password: str
    recipient_email: str
    user_prompt: str  # Natural language prompt like "Send internship mail"

# --- WebSocket Pub/Sub for Screenshot Streaming ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.warning(f"Error sending to WebSocket: {e}")

manager = ConnectionManager()

@app.websocket("/ws/screenshots/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            await asyncio.sleep(60)  # Keep connection open
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

# --- Utility to notify WebSocket clients when a screenshot is created ---
def notify_screenshot(session_id: str, screenshot: dict):
    """Notify WebSocket clients about new screenshot"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast(session_id, screenshot))
        else:
            loop.run_until_complete(manager.broadcast(session_id, screenshot))
    except Exception as e:
        logger.warning(f"Error notifying screenshot: {e}")

@app.get("/")
async def root():
    return {"message": "AI Email Agent v2 - Intelligent Gmail Automation with AI"}

@app.get("/test")
async def test_endpoint():
    """Test endpoint to check if the API is working"""
    return {"status": "success", "message": "AI Email Agent v2 API is working correctly!"}

@app.post("/send-ai-email")
async def send_ai_email(request: AIEmailRequest):
    """Send email using AI-powered automation with natural language prompts"""
    try:
        logger.info(f"Starting AI-powered email automation")
        
        # Initialize the AI-powered email agent
        email_agent = AIEmailAgent()
        
        # Attempt to send email using AI automation
        try:
            logger.info("Attempting AI-powered automation...")
            result = email_agent.send_email(
                gmail_id=request.gmail_id,
                gmail_password=request.gmail_password,
                recipient_email=request.recipient_email,
                user_prompt=request.user_prompt
            )
            
            if result["status"] == "success":
                logger.info("AI-powered email sent successfully!")
                return {
                    "status": "success",
                    "message": "✅ Email sent successfully using AI-generated content!",
                    "screenshots": result["screenshots"],
                    "session_id": result["session_id"],
                    "email_content": result.get("email_content", {}),
                    "ai_generated": result.get("ai_generated", True)
                }
            else:
                logger.error(f"AI automation failed: {result['message']}")
                # Fall back to demo mode
                raise Exception(f"AI automation failed: {result['message']}")
                
        except Exception as ai_error:
            logger.error(f"AI automation failed: {ai_error}")
            
            # Fall back to demo mode
            logger.info("Falling back to AI demo mode...")
            import uuid
            session_id = str(uuid.uuid4())
            demo_screenshots = create_ai_demo_screenshots(session_id)
            
            # Notify WebSocket clients about demo screenshots
            for screenshot in demo_screenshots:
                notify_screenshot(session_id, screenshot)
            
            return {
                "status": "demo",
                "message": "🎭 Demo Mode: AI-powered email automation simulation. Showing AI analysis and content generation steps.",
                "screenshots": demo_screenshots,
                "session_id": session_id,
                "ai_generated": True,
                "error": str(ai_error)
            }
            
    except Exception as e:
        logger.error(f"AI email automation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AI Email Agent v2 is running"}

if __name__ == "__main__":
    import uvicorn
    # Use import string for reload to work properly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 