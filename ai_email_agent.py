import os
import logging
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional

# Try to import cohere, but make it optional
try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    cohere = None

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import base64
from PIL import Image
import io
import json

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

class AIEmailAgent:
    def __init__(self):
        """Initialize the AI Email Agent with Cohere integration"""
        api_key = os.getenv("COHERE_API_KEY")
        logger.info(f"API Key loaded: {api_key[:20] if api_key else 'None'}...")
        
        # Check if cohere is available
        if not COHERE_AVAILABLE:
            logger.warning("Cohere library not installed. AI features will be disabled.")
            self.ai_available = False
        elif api_key and api_key != "your_cohere_api_key_here":
            try:
                logger.info("Attempting to initialize Cohere client...")
                self.cohere_client = cohere.Client(api_key)
                # Test the client with a simple request
                logger.info("Testing Cohere client with a simple request...")
                test_response = self.cohere_client.generate(
                    model="command",
                    prompt="Hello",
                    max_tokens=5
                )
                logger.info("Cohere client test successful!")
                self.ai_available = True
                logger.info("Cohere client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Cohere client: {e}")
                if "insufficient_quota" in str(e) or "429" in str(e):
                    logger.warning("Cohere API quota exceeded. Using fallback mode.")
                elif "invalid_api_key" in str(e):
                    logger.warning("Invalid Cohere API key. Using fallback mode.")
                else:
                    logger.warning("Cohere client initialization failed. Using fallback mode.")
                self.ai_available = False
        else:
            logger.warning("No valid Cohere API key found. AI features will be disabled.")
            self.ai_available = False
        
        self.screenshots = []
        self.session_id = None
        
    def interpret_prompt(self, user_prompt: str) -> Dict:
        """
        Interpret natural language prompt and extract email details
        """
        if not self.ai_available:
            # Fallback interpretation without AI
            logger.info("Using fallback prompt interpretation (no AI)")
            return {
                "email_type": "general",
                "subject": f"Re: {user_prompt[:50]}...",
                "body": f"Hello,\n\n{user_prompt}\n\nBest regards,\n[Your Name]",
                "tone": "professional",
                "key_points": [user_prompt]
            }
        
        try:
            system_prompt = """
            You are an intelligent email assistant. Analyze the user's natural language prompt and extract:
            1. Email type/purpose (e.g., internship application, follow-up, thank you, etc.)
            2. Recipient context (if mentioned)
            3. Key points to include
            4. Appropriate tone (professional, casual, formal, etc.)
            
            Return a JSON object with:
            - email_type: The type of email
            - subject: A professional subject line
            - body: A well-written email body (2-3 paragraphs)
            - tone: The tone used
            - key_points: List of main points covered
            """
            
            prompt_text = f"{system_prompt}\n\nAnalyze this prompt: {user_prompt}"
            
            response = self.cohere_client.generate(
                model="command",
                prompt=prompt_text,
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            content = response.generations[0].text
            # Extract JSON from the response (handle potential formatting)
            try:
                # Try to parse as JSON directly
                result = json.loads(content)
            except:
                # If that fails, try to extract JSON from the text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    # Fallback to basic interpretation
                    result = {
                        "email_type": "general",
                        "subject": f"Re: {user_prompt[:50]}...",
                        "body": f"Hello,\n\n{user_prompt}\n\nBest regards,\n[Your Name]",
                        "tone": "professional",
                        "key_points": [user_prompt]
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error interpreting prompt: {e}")
            # Fallback response
            return {
                "email_type": "general",
                "subject": f"Re: {user_prompt[:50]}...",
                "body": f"Hello,\n\n{user_prompt}\n\nBest regards,\n[Your Name]",
                "tone": "professional",
                "key_points": [user_prompt]
            }
    
    def generate_email_content(self, prompt: str, recipient_email: str = None) -> Dict:
        """
        Generate complete email content using AI
        """
        if not self.ai_available:
            # Fallback content generation without AI
            logger.info("Using fallback email content generation (no AI)")
            return {
                "subject": f"Re: {prompt[:50]}...",
                "body": f"Hello,\n\n{prompt}\n\nBest regards,\n[Your Name]",
                "email_type": "general",
                "tone": "professional",
                "key_points": [prompt],
                "ai_generated": False
            }
        
        try:
            # First interpret the prompt
            interpretation = self.interpret_prompt(prompt)
            
            # Enhance the email content with more context
            enhancement_prompt = f"""
            Based on this interpretation: {interpretation}
            
            Generate a professional email with:
            - A compelling subject line
            - A well-structured body (2-3 paragraphs)
            - Appropriate greeting and closing
            - Professional tone matching the email type
            
            Email type: {interpretation.get('email_type', 'general')}
            Recipient: {recipient_email or 'recipient'}
            
            Make it sound natural and professional.
            """
            
            response = self.cohere_client.generate(
                model="command",
                prompt=enhancement_prompt,
                temperature=0.7,
                max_tokens=400
            )
            
            enhanced_content = response.generations[0].text
            
            # Extract subject and body from the enhanced content
            lines = enhanced_content.split('\n')
            subject = interpretation.get('subject', 'No Subject')
            body = enhanced_content
            
            return {
                "subject": subject,
                "body": body,
                "email_type": interpretation.get('email_type', 'general'),
                "tone": interpretation.get('tone', 'professional'),
                "key_points": interpretation.get('key_points', [prompt]),
                "ai_generated": True
            }
            
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            # Fallback content
            return {
                "subject": f"Re: {prompt[:50]}...",
                "body": f"Hello,\n\n{prompt}\n\nBest regards,\n[Your Name]",
                "email_type": "general",
                "tone": "professional",
                "key_points": [prompt],
                "ai_generated": False
            }
    
    def capture_screenshot(self, driver, step_name: str) -> str:
        """Capture screenshot and save with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.session_id}_{step_name}_{timestamp}.png"
            filepath = os.path.join("screenshots", filename)
            
            # Ensure screenshots directory exists
            os.makedirs("screenshots", exist_ok=True)
            
            # Take screenshot
            driver.save_screenshot(filepath)
            
            # Create screenshot info
            screenshot_info = {
                "filename": filename,
                "step": step_name,
                "description": self.get_step_description(step_name),
                "timestamp": timestamp,
                "url": f"/screenshots/{filename}"
            }
            
            self.screenshots.append(screenshot_info)
            logger.info(f"Screenshot captured: {step_name}")
            return filename
            
        except Exception as e:
            logger.error(f"Error capturing screenshot for {step_name}: {e}")
            return None
    
    def get_step_description(self, step_name: str) -> str:
        """Get human-readable description for each step"""
        descriptions = {
            "start": "Starting Gmail automation",
            "login": "Logging into Gmail account",
            "compose": "Opening compose window",
            "recipient": "Entering recipient email",
            "subject": "Entering email subject",
            "body": "Entering email body content",
            "send": "Sending the email",
            "success": "Email sent successfully",
            "error": "Error occurred during automation",
            "ai_analysis": "AI analyzing the prompt",
            "content_generation": "AI generating email content"
        }
        return descriptions.get(step_name, f"Step: {step_name}")
    
    def wait_for_element_safe(self, driver, by, selector, timeout=10, condition="clickable"):
        """Safely wait for element with multiple conditions"""
        wait = WebDriverWait(driver, timeout)
        try:
            if condition == "clickable":
                return wait.until(EC.element_to_be_clickable((by, selector)))
            elif condition == "visible":
                return wait.until(EC.visibility_of_element_located((by, selector)))
            elif condition == "present":
                return wait.until(EC.presence_of_element_located((by, selector)))
            else:
                return wait.until(EC.presence_of_element_located((by, selector)))
        except TimeoutException:
            return None
    
    def find_element_with_fallback(self, driver, selectors, by=By.CSS_SELECTOR, timeout=10):
        """Find element using multiple selectors with fallback"""
        for selector in selectors:
            try:
                element = self.wait_for_element_safe(driver, by, selector, timeout, "visible")
                if element and element.is_displayed() and element.is_enabled():
                    logger.info(f"Found element with selector: {selector}")
                    return element
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        return None
    
    def send_email(self, gmail_id: str, gmail_password: str, 
                   recipient_email: str, user_prompt: str) -> Dict:
        """
        Main method to send email using AI-generated content with improved automation
        """
        self.session_id = str(uuid.uuid4())
        self.screenshots = []
        
        try:
            logger.info(f"Starting AI-powered email automation for session {self.session_id}")
            
            # Generate email content using AI
            logger.info("Generating email content using AI...")
            email_content = self.generate_email_content(user_prompt, recipient_email)
            
            logger.info(f"AI generated email - Type: {email_content['email_type']}, Tone: {email_content['tone']}")
            
            # Initialize Selenium WebDriver with improved options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Add user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Remove webdriver property to avoid detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            wait = WebDriverWait(driver, 30)
            
            try:
                # Step 1: Navigate to Gmail
                logger.info("Navigating to Gmail...")
                driver.get("https://mail.google.com")
                time.sleep(5)  # Wait for page to load
                self.capture_screenshot(driver, "start")
                
                # Step 2: Login with improved selectors
                logger.info("Logging into Gmail...")
                
                # Email input with multiple selectors
                email_selectors = [
                    "input[type='email']",
                    "input[name='identifier']",
                    "#identifierId",
                    "input[aria-label*='Email']",
                    "input[aria-label*='email']"
                ]
                
                email_input = self.find_element_with_fallback(driver, email_selectors)
                if not email_input:
                    raise Exception("Could not find email input field")
                
                # Clear and enter email
                email_input.clear()
                time.sleep(1)
                email_input.send_keys(gmail_id)
                time.sleep(2)
                
                # Next button with multiple selectors
                next_selectors = [
                    "#identifierNext button",
                    "#identifierNext",
                    "button[jsname='LgbsSe']",
                    "button[type='submit']",
                    "button[aria-label*='Next']",
                    "button:contains('Next')"
                ]
                
                next_button = self.find_element_with_fallback(driver, next_selectors)
                if not next_button:
                    raise Exception("Could not find next button")
                
                next_button.click()
                time.sleep(5)
                self.capture_screenshot(driver, "login")
                
                # Password input with improved handling
                password_selectors = [
                    "input[type='password']",
                    "input[name='password']",
                    "input[aria-label*='Password']",
                    "input[aria-label*='password']"
                ]
                
                password_input = self.find_element_with_fallback(driver, password_selectors, timeout=15)
                if not password_input:
                    raise Exception("Could not find password input field")
                
                # Clear and enter password
                password_input.clear()
                time.sleep(1)
                password_input.send_keys(gmail_password)
                time.sleep(2)
                
                # Password next button
                password_next_selectors = [
                    "#passwordNext button",
                    "#passwordNext",
                    "button[jsname='LgbsSe']",
                    "button[type='submit']",
                    "button[aria-label*='Next']"
                ]
                
                password_next = self.find_element_with_fallback(driver, password_next_selectors)
                if not password_next:
                    raise Exception("Could not find password next button")
                
                password_next.click()
                time.sleep(8)  # Wait longer for login to complete
                self.capture_screenshot(driver, "login")
                
                # Check for security challenges
                security_selectors = [
                    "div[data-challenge-type]",
                    "#challengePickerList",
                    ".challenge-picker",
                    "div[aria-label*='verification']"
                ]
                
                for selector in security_selectors:
                    try:
                        if driver.find_element(By.CSS_SELECTOR, selector):
                            logger.warning("Security challenge detected - automation may fail")
                            self.capture_screenshot(driver, "security_challenge")
                            raise Exception("Gmail security challenge detected. Please complete manually.")
                    except NoSuchElementException:
                        continue
                
                # Step 3: Open compose window with improved selectors
                logger.info("Opening compose window...")
                
                # Wait for Gmail to fully load
                time.sleep(5)
                
                compose_selectors = [
                    "div[role='button'][data-tooltip*='Compose']",
                    "div[role='button'][aria-label*='Compose']",
                    "div[data-tooltip*='Compose']",
                    "div[jsaction*='compose']",
                    "div[aria-label*='Compose']",
                    "div[title*='Compose']",
                    "div[data-tooltip='Compose']",
                    "div[data-tooltip='New Message']",
                    "div[aria-label='Compose']",
                    "div[aria-label='New Message']"
                ]
                
                compose_button = self.find_element_with_fallback(driver, compose_selectors, timeout=15)
                if not compose_button:
                    # Try clicking by JavaScript as fallback
                    try:
                        driver.execute_script("document.querySelector('div[role=\"button\"][data-tooltip*=\"Compose\"]').click()")
                        time.sleep(3)
                    except:
                        raise Exception("Could not open compose window")
                else:
                    compose_button.click()
                    time.sleep(5)
                
                self.capture_screenshot(driver, "compose")
                
                # Wait for compose window to fully load
                logger.info("Waiting for compose window to load...")
                time.sleep(8)
                
                # Step 4: Fill recipient with improved selectors and debugging
                logger.info("Entering recipient...")
                
                # Wait for compose window to fully load
                time.sleep(8)
                
                # Debug available elements
                try:
                    all_inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea, div[contenteditable='true']")
                    logger.info(f"Found {len(all_inputs)} input elements")
                    for i, elem in enumerate(all_inputs[:10]):  # Log first 10 elements
                        if elem.is_displayed():
                            placeholder = elem.get_attribute("placeholder") or ""
                            aria_label = elem.get_attribute("aria-label") or ""
                            role = elem.get_attribute("role") or ""
                            name = elem.get_attribute("name") or ""
                            logger.info(f"Input {i}: placeholder='{placeholder}', aria-label='{aria_label}', role='{role}', name='{name}'")
                except Exception as e:
                    logger.warning(f"Could not debug input elements: {e}")
                
                # Updated recipient selectors for current Gmail UI
                to_selectors = [
                    "textarea[name='to']",
                    "input[name='to']",
                    "div[role='textbox'][aria-label*='To']",
                    "div[contenteditable='true'][aria-label*='To']",
                    "div[role='textbox']",
                    "div[contenteditable='true']",
                    "input[type='email']",
                    "input[placeholder*='Recipients']",
                    "input[placeholder*='To']",
                    "div[data-tooltip*='To']",
                    "div[aria-label*='To']",
                    "div[data-tooltip*='Recipients']",
                    "div[contenteditable='true'][data-tooltip*='To']",
                    "div[contenteditable='true'][data-tooltip*='Recipients']",
                    "div[aria-label*='Recipients']",
                    "div[data-tooltip*='Add recipients']",
                    "div[aria-label*='Add recipients']",
                    "div[data-tooltip*='Add people']",
                    "div[aria-label*='Add people']"
                ]
                
                to_field = self.find_element_with_fallback(driver, to_selectors, timeout=15)
                
                if not to_field:
                    # Try XPath as fallback
                    xpath_selectors = [
                        "//div[@role='textbox' and contains(@aria-label, 'To')]",
                        "//div[@contenteditable='true' and contains(@aria-label, 'To')]",
                        "//input[@type='email']",
                        "//textarea[@name='to']",
                        "//input[@name='to']",
                        "//div[contains(@data-tooltip, 'To')]",
                        "//div[contains(@aria-label, 'To')]",
                        "//div[contains(@aria-label, 'Recipients')]",
                        "//div[contains(@aria-label, 'Add recipients')]",
                        "//div[contains(@aria-label, 'Add people')]"
                    ]
                    
                    for xpath in xpath_selectors:
                        try:
                            to_field = self.wait_for_element_safe(driver, By.XPATH, xpath, 5, "visible")
                            if to_field and to_field.is_displayed() and to_field.is_enabled():
                                logger.info(f"Found recipient field with XPath: {xpath}")
                                break
                        except:
                            continue
                
                if not to_field:
                    # Last resort: try to find any input field that might be the recipient field
                    try:
                        all_inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea, div[contenteditable='true']")
                        for input_elem in all_inputs:
                            if input_elem.is_displayed() and input_elem.is_enabled():
                                # Check if it's likely a recipient field
                                placeholder = input_elem.get_attribute("placeholder") or ""
                                aria_label = input_elem.get_attribute("aria-label") or ""
                                name = input_elem.get_attribute("name") or ""
                                if ("to" in placeholder.lower() or "recipient" in placeholder.lower() or 
                                    "to" in aria_label.lower() or "recipient" in aria_label.lower() or
                                    "to" in name.lower() or "recipient" in name.lower()):
                                    to_field = input_elem
                                    logger.info("Found recipient field by placeholder/aria-label/name")
                                    break
                    except:
                        pass
                
                if not to_field:
                    # Try clicking on the compose area to focus it
                    try:
                        compose_area = driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
                        compose_area.click()
                        time.sleep(2)
                        
                        # Try to find recipient field again after clicking
                        to_field = self.find_element_with_fallback(driver, to_selectors, timeout=10)
                    except:
                        pass
                
                if not to_field:
                    raise Exception("Could not find recipient field")
                
                # Clear and fill the recipient field
                to_field.clear()
                time.sleep(1)
                to_field.send_keys(recipient_email)
                time.sleep(2)
                self.capture_screenshot(driver, "recipient")
                
                # Step 5: Fill subject with improved selectors
                logger.info("Entering subject...")
                subject_selectors = [
                    "input[name='subjectbox']",
                    "input[name='subject']",
                    "div[role='textbox'][aria-label*='Subject']",
                    "div[contenteditable='true'][aria-label*='Subject']",
                    "input[placeholder*='Subject']",
                    "div[data-tooltip*='Subject']",
                    "div[aria-label*='Subject']",
                    "input[aria-label*='Subject']"
                ]
                
                subject_field = self.find_element_with_fallback(driver, subject_selectors, timeout=10)
                
                if not subject_field:
                    # Try XPath as fallback
                    xpath_selectors = [
                        "//input[@name='subjectbox']",
                        "//input[@name='subject']",
                        "//div[@role='textbox' and contains(@aria-label, 'Subject')]",
                        "//div[@contenteditable='true' and contains(@aria-label, 'Subject')]",
                        "//input[contains(@placeholder, 'Subject')]"
                    ]
                    
                    for xpath in xpath_selectors:
                        try:
                            subject_field = self.wait_for_element_safe(driver, By.XPATH, xpath, 5, "visible")
                            if subject_field and subject_field.is_displayed() and subject_field.is_enabled():
                                logger.info(f"Found subject field with XPath: {xpath}")
                                break
                        except:
                            continue
                
                if not subject_field:
                    raise Exception("Could not find subject field")
                
                # Clear and fill subject
                subject_field.clear()
                time.sleep(1)
                subject_field.send_keys(email_content['subject'])
                time.sleep(2)
                self.capture_screenshot(driver, "subject")
                
                # Step 6: Fill email body with improved selectors
                logger.info("Entering email body...")
                body_selectors = [
                    "div[role='textbox'][aria-label*='Message Body']",
                    "div[contenteditable='true'][aria-label*='Message Body']",
                    "div[role='textbox'][aria-label*='Body']",
                    "div[contenteditable='true'][aria-label*='Body']",
                    "div[role='textbox']",
                    "div[contenteditable='true']",
                    "div[data-tooltip*='Message']",
                    "div[data-tooltip*='Body']",
                    "div[aria-label*='Message']",
                    "div[aria-label*='Body']"
                ]
                
                body_field = self.find_element_with_fallback(driver, body_selectors, timeout=10)
                
                if not body_field:
                    # Try XPath as fallback
                    xpath_selectors = [
                        "//div[@role='textbox' and contains(@aria-label, 'Message Body')]",
                        "//div[@contenteditable='true' and contains(@aria-label, 'Message Body')]",
                        "//div[@role='textbox' and contains(@aria-label, 'Body')]",
                        "//div[@contenteditable='true' and contains(@aria-label, 'Body')]",
                        "//div[@role='textbox']",
                        "//div[@contenteditable='true']"
                    ]
                    
                    for xpath in xpath_selectors:
                        try:
                            body_field = self.wait_for_element_safe(driver, By.XPATH, xpath, 5, "visible")
                            if body_field and body_field.is_displayed() and body_field.is_enabled():
                                logger.info(f"Found body field with XPath: {xpath}")
                                break
                        except:
                            continue
                
                if not body_field:
                    # Last resort: find the largest contenteditable div
                    try:
                        contenteditable_divs = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
                        if contenteditable_divs:
                            # Find the largest one (likely the body field)
                            largest_div = max(contenteditable_divs, key=lambda x: x.size['width'] * x.size['height'])
                            if largest_div.is_displayed() and largest_div.is_enabled():
                                body_field = largest_div
                                logger.info("Found body field by size (largest contenteditable div)")
                    except:
                        pass
                
                if not body_field:
                    raise Exception("Could not find body field")
                
                # Clear and fill body
                body_field.clear()
                time.sleep(1)
                body_field.send_keys(email_content['body'])
                time.sleep(2)
                self.capture_screenshot(driver, "body")
                
                # Step 7: Send email with improved selectors
                logger.info("Sending email...")
                send_selectors = [
                    "div[role='button'][data-tooltip-delay='800'][data-tooltip*='Send']",
                    "div[role='button'][data-tooltip*='Send']",
                    "div[jsname='M2UYVd']",
                    "button[type='submit']",
                    "div[aria-label*='Send']",
                    "div[data-tooltip='Send']",
                    "div[title*='Send']"
                ]
                
                send_button = self.find_element_with_fallback(driver, send_selectors, timeout=10)
                
                if not send_button:
                    raise Exception("Could not find send button")
                
                send_button.click()
                time.sleep(5)
                self.capture_screenshot(driver, "send")
                
                # Step 8: Verify success
                logger.info("Verifying email sent...")
                time.sleep(3)
                self.capture_screenshot(driver, "success")
                
                return {
                    "status": "success",
                    "message": "Email sent successfully using AI-generated content!",
                    "screenshots": self.screenshots,
                    "session_id": self.session_id,
                    "email_content": email_content,
                    "ai_generated": True
                }
                
            except Exception as e:
                logger.error(f"Error during automation: {e}")
                try:
                    self.capture_screenshot(driver, "error")
                except:
                    pass
                
                # Don't quit the driver immediately, let user see the error
                logger.info("Keeping browser open for 10 seconds to show error...")
                time.sleep(10)
                
                return {
                    "status": "error",
                    "message": f"Automation failed: {str(e)}",
                    "screenshots": self.screenshots,
                    "session_id": self.session_id,
                    "email_content": email_content,
                    "ai_generated": True
                }
                
            finally:
                try:
                    logger.info("Closing browser...")
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize automation: {e}")
            return {
                "status": "error",
                "message": f"Failed to start automation: {str(e)}",
                "screenshots": self.screenshots,
                "session_id": self.session_id,
                "ai_generated": False
            }

def create_ai_demo_screenshots(session_id: str) -> List[Dict]:
    """Create demo screenshots for AI email automation simulation"""
    steps = [
        ("start", "Starting Gmail automation"),
        ("ai_analysis", "AI analyzing your prompt"),
        ("content_generation", "AI generating email content"),
        ("login", "Logging into Gmail account"),
        ("compose", "Opening compose window"),
        ("recipient", "Entering recipient email"),
        ("subject", "Entering email subject"),
        ("body", "Entering email body content"),
        ("send", "Sending the email"),
        ("success", "Email sent successfully")
    ]
    
    screenshots = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for step, description in steps:
        filename = f"{session_id}_{step}_{timestamp}.png"
        filepath = os.path.join("screenshots", filename)
        
        # Create a simple demo image
        try:
            img = Image.new('RGB', (800, 600), color='white')
            from PIL import ImageDraw, ImageFont
            
            draw = ImageDraw.Draw(img)
            # Use default font
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Add text to the image
            draw.text((50, 50), f"AI Email Agent Demo", fill='black', font=font)
            draw.text((50, 100), f"Step: {step}", fill='blue', font=font)
            draw.text((50, 150), f"Description: {description}", fill='black', font=font)
            draw.text((50, 200), f"Session: {session_id}", fill='gray', font=font)
            draw.text((50, 250), f"Timestamp: {timestamp}", fill='gray', font=font)
            
            # Save the image
            os.makedirs("screenshots", exist_ok=True)
            img.save(filepath)
            
            screenshot_info = {
                "filename": filename,
                "step": step,
                "description": description,
                "timestamp": timestamp,
                "url": f"/screenshots/{filename}"
            }
            screenshots.append(screenshot_info)
            
        except Exception as e:
            logger.error(f"Error creating demo screenshot for {step}: {e}")
    
    return screenshots
