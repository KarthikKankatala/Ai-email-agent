from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from email_agent_selenium import EmailAgentSelenium, create_demo_screenshots

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Email Agent", description="Automate Gmail email sending with screenshots")

# Add CORS middleware - updated to include port 5174
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

class EmailRequest(BaseModel):
    gmail_id: str
    gmail_password: str
    recipient_email: str
    subject: str
    body: str

@app.get("/")
async def root():
    return {"message": "AI Email Agent API is running!"}

@app.get("/test")
async def test_endpoint():
    """Test endpoint to check if the API is working"""
    return {"status": "success", "message": "API is working correctly!"}

@app.post("/send-email")
async def send_email(request: EmailRequest):
    """Send email using Gmail automation with Selenium"""
    try:
        logger.info(f"Starting email automation for session")
        
        # Initialize the Selenium-based email agent
        email_agent = EmailAgentSelenium()
        
        # Attempt to send email using Selenium
        try:
            logger.info("Attempting Selenium automation...")
            result = email_agent.send_email(
                gmail_id=request.gmail_id,
                gmail_password=request.gmail_password,
                recipient_email=request.recipient_email,
                subject=request.subject,
                body=request.body
            )
            
            if result["status"] == "success":
                logger.info("Email sent successfully using Selenium!")
                return result
            else:
                logger.error(f"Selenium automation failed: {result['message']}")
                # Fall back to demo mode
                raise Exception(f"Selenium automation failed: {result['message']}")
                
        except Exception as selenium_error:
            logger.error(f"Selenium automation failed: {selenium_error}")
            
            # Fall back to demo mode
            logger.info("Falling back to demo mode...")
            import uuid
            session_id = str(uuid.uuid4())
            demo_screenshots = create_demo_screenshots(session_id)
            
            return {
                "status": "demo",
                "message": "Demo mode: Selenium automation not available. Showing simulated screenshots.",
                "screenshots": demo_screenshots,
                "session_id": session_id,
                "error": str(selenium_error)
            }
            
    except Exception as e:
        logger.error(f"Email automation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AI Email Agent is running"}

if __name__ == "__main__":
    import uvicorn
    # Use import string for reload to work properly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 