import os
import time
import uuid
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailAgentSelenium:
    def __init__(self):
        self.driver = None
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options for Windows"""
        try:
            chrome_options = Options()
            
            # Windows-specific options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            chrome_options.add_argument("--disable-javascript")  # Disable JS for faster loading
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set Chrome binary path for Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', ''))
            ]
            
            chrome_found = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    chrome_options.binary_location = chrome_path
                    logger.info(f"Using Chrome at: {chrome_path}")
                    chrome_found = True
                    break
            
            if not chrome_found:
                logger.warning("Chrome not found at expected locations, using system default")
            
            # Use webdriver-manager to automatically download and manage ChromeDriver
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Chrome driver setup successful with webdriver-manager")
            except Exception as e:
                logger.warning(f"webdriver-manager failed: {e}")
                # Fallback to system ChromeDriver
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    logger.info("Chrome driver setup successful with system ChromeDriver")
                except Exception as e2:
                    logger.error(f"System ChromeDriver also failed: {e2}")
                    return False
            
            # Remove webdriver property to avoid detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome driver setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def take_screenshot(self, session_id, step_name):
        """Take a screenshot and save it"""
        try:
            if not os.path.exists(f"{self.screenshots_dir}/{session_id}"):
                os.makedirs(f"{self.screenshots_dir}/{session_id}")
            
            filename = f"{self.screenshots_dir}/{session_id}/{step_name}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return f"/screenshots/{session_id}/{step_name}.png"
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Element not found: {by}={value}")
            return None
    
    def send_email(self, gmail_id, gmail_password, recipient_email, subject, body):
        """Send email using Gmail web interface"""
        session_id = str(uuid.uuid4())
        screenshots = []
        
        try:
            logger.info(f"Starting email automation for session: {session_id}")
            
            # Setup driver
            if not self.setup_driver():
                raise Exception("Failed to setup Chrome driver")
            
            # Step 1: Navigate to Gmail
            logger.info("Step 1: Navigating to Gmail")
            self.driver.get("https://mail.google.com")
            time.sleep(3)
            
            screenshot_path = self.take_screenshot(session_id, "1_gmail_login")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            # Step 2: Enter email
            logger.info("Step 2: Entering email address")
            email_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='email']")
            if not email_input:
                # Try alternative selectors
                email_input = self.wait_for_element(By.NAME, "identifier")
            
            if email_input:
                email_input.clear()
                email_input.send_keys(gmail_id)
                time.sleep(1)
                
                # Click Next
                next_button = self.wait_for_element(By.CSS_SELECTOR, "#identifierNext button")
                if next_button:
                    next_button.click()
                    time.sleep(3)
                else:
                    # Try alternative next button
                    next_button = self.wait_for_element(By.XPATH, "//span[text()='Next']")
                    if next_button:
                        next_button.click()
                        time.sleep(3)
            else:
                raise Exception("Could not find email input field")
            
            screenshot_path = self.take_screenshot(session_id, "2_enter_email")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            # Step 3: Enter password
            logger.info("Step 3: Entering password")
            password_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='password']")
            if not password_input:
                # Try alternative selectors
                password_input = self.wait_for_element(By.NAME, "password")
            
            if password_input:
                password_input.clear()
                password_input.send_keys(gmail_password)
                time.sleep(1)
                
                # Click Next
                next_button = self.wait_for_element(By.CSS_SELECTOR, "#passwordNext button")
                if next_button:
                    next_button.click()
                    time.sleep(5)
                else:
                    # Try alternative next button
                    next_button = self.wait_for_element(By.XPATH, "//span[text()='Next']")
                    if next_button:
                        next_button.click()
                        time.sleep(5)
            else:
                raise Exception("Could not find password input field")
            
            screenshot_path = self.take_screenshot(session_id, "3_enter_password")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            # Step 4: Wait for Gmail to load and click Compose
            logger.info("Step 4: Clicking Compose button")
            compose_button = None
            compose_selectors = [
                "div[role='button'][gh='cm']",
                "div[role='button'][data-tooltip*='Compose']",
                "div[role='button'][aria-label*='Compose']",
                "div[data-tooltip*='Compose']",
                "div[aria-label*='Compose']"
            ]
            
            for selector in compose_selectors:
                compose_button = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=3)
                if compose_button:
                    logger.info(f"Found compose button with selector: {selector}")
                    break
            
            if not compose_button:
                # Try XPath selectors as fallback
                xpath_selectors = [
                    "//div[contains(text(), 'Compose')]",
                    "//div[@role='button' and contains(text(), 'Compose')]",
                    "//div[contains(@aria-label, 'Compose')]",
                    "//div[contains(@data-tooltip, 'Compose')]",
                    "//span[contains(text(), 'Compose')]"
                ]
                for xpath in xpath_selectors:
                    compose_button = self.wait_for_element(By.XPATH, xpath, timeout=3)
                    if compose_button:
                        logger.info(f"Found compose button with XPath: {xpath}")
                        break
            
            if compose_button:
                compose_button.click()
                time.sleep(3)
                logger.info("Clicked compose button successfully")
            else:
                raise Exception("Could not find Compose button")

            # Try clicking the 'To' label/area to activate the input
            try:
                to_label = self.wait_for_element(By.XPATH, "//span[contains(text(), 'To') or contains(text(), 'Recipients') or contains(text(), 'recipients') or contains(text(), 'to') or contains(text(), 'TO') or contains(text(), 'TO:') or contains(text(), 'To:')]", timeout=2)
                if to_label:
                    to_label.click()
                    logger.info("Clicked the 'To' label/area to activate input")
                    time.sleep(1)
            except Exception as e:
                logger.debug(f"Could not click 'To' label/area: {e}")

            # Log all input fields after clicking Compose for debugging
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                logger.info(f"Input field: id={inp.get_attribute('id')}, class={inp.get_attribute('class')}, aria-label={inp.get_attribute('aria-label')}")

            # Step 5: Fill in email details
            logger.info("Step 5: Filling email details")

            # Recipient - try multiple selectors (ID, class, aria-label)
            to_input = None
            to_selectors = [
                "#\\:1gg",  # Escaped ID selector (update dynamically if needed)
                "input[aria-label='To recipients']",
                "input.agP.aFw",
                "input.agP",
                "input.aFw",
                "input[type='text'][aria-label*='To']",
                "input[type='text']"
            ]

            for selector in to_selectors:
                try:
                    to_input = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=2)
                    if to_input:
                        logger.info(f"Found recipient field with selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")

            if not to_input:
                logger.warning("Recipient field not found with any selector. Trying fallback by scanning all input fields...")
                # Fallback: try to find by class or aria-label in all input fields
                for inp in all_inputs:
                    if (inp.get_attribute('aria-label') and 'To recipient' in inp.get_attribute('aria-label')) or \
                       ('agP' in inp.get_attribute('class') and 'aFw' in inp.get_attribute('class')):
                        to_input = inp
                        logger.info(f"Fallback: Found recipient field by scanning inputs: id={inp.get_attribute('id')}, class={inp.get_attribute('class')}")
                        break

            if to_input:
                try:
                    to_input.click()
                    time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"Could not click recipient field: {e}")
                try:
                    to_input.clear()
                except Exception as e:
                    logger.debug(f"Could not clear recipient field: {e}")
                try:
                    to_input.send_keys(recipient_email)
                    time.sleep(0.5)
                    to_input.send_keys(Keys.ENTER)
                    time.sleep(1)
                    logger.info(f"Entered recipient email and confirmed: {recipient_email}")
                except Exception as e:
                    logger.warning(f"Could not send keys to recipient field: {e}. Trying JS fallback.")
                    # Fallback: use JS to set value
                    self.driver.execute_script("arguments[0].value = arguments[1];", to_input, recipient_email)
                    logger.info(f"Set recipient email via JS: {recipient_email}")
            else:
                logger.error("Could not find recipient field. Email will not be sent.")
                self.save_screenshot(session_dir, "5_filled_email.png")
                self.quit_driver()
                raise Exception("Could not find recipient field in Gmail compose window.")
            
            # Subject - try multiple selectors
            subject_input = None
            subject_selectors = [
                "input[name='subjectbox']",
                "input[placeholder*='Subject']",
                "div[role='textbox'][aria-label*='Subject']",
                "div[contenteditable='true'][aria-label*='Subject']",
                "input[name='subject']"
            ]
            
            for selector in subject_selectors:
                subject_input = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=3)
                if subject_input:
                    logger.info(f"Found subject field with selector: {selector}")
                    break
            
            if not subject_input:
                # Try XPath selectors as fallback
                xpath_selectors = [
                    "//input[contains(@placeholder, 'Subject')]",
                    "//div[@contenteditable='true' and contains(@aria-label, 'Subject')]",
                    "//div[@role='textbox' and contains(@aria-label, 'Subject')]"
                ]
                for xpath in xpath_selectors:
                    subject_input = self.wait_for_element(By.XPATH, xpath, timeout=3)
                    if subject_input:
                        logger.info(f"Found subject field with XPath: {xpath}")
                        break
            
            if subject_input:
                subject_input.clear()
                subject_input.send_keys(subject)
                time.sleep(1)
                logger.info(f"Entered subject: {subject}")
            else:
                logger.warning("Could not find subject field, but continuing...")
            
            # Body - try multiple selectors
            body_input = None
            body_selectors = [
                "div[role='textbox']",
                "div[contenteditable='true'][aria-label*='Message']",
                "div[contenteditable='true'][aria-label*='Body']",
                "div[role='textbox'][aria-label*='Message']",
                "div[role='textbox'][aria-label*='Body']",
                "div[data-tooltip*='Message']",
                "div[data-tooltip*='Body']"
            ]
            
            for selector in body_selectors:
                body_input = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=3)
                if body_input:
                    logger.info(f"Found body field with selector: {selector}")
                    break
            
            if not body_input:
                # Try XPath selectors as fallback
                xpath_selectors = [
                    "//div[@contenteditable='true' and contains(@aria-label, 'Message')]",
                    "//div[@contenteditable='true' and contains(@aria-label, 'Body')]",
                    "//div[@role='textbox' and contains(@aria-label, 'Message')]",
                    "//div[@role='textbox' and contains(@aria-label, 'Body')]",
                    "//div[@contenteditable='true' and not(contains(@aria-label, 'To')) and not(contains(@aria-label, 'Subject'))]"
                ]
                for xpath in xpath_selectors:
                    body_input = self.wait_for_element(By.XPATH, xpath, timeout=3)
                    if body_input:
                        logger.info(f"Found body field with XPath: {xpath}")
                        break
            
            if body_input:
                body_input.clear()
                body_input.send_keys(body)
                time.sleep(1)
                logger.info(f"Entered body text: {body[:50]}...")
            else:
                logger.warning("Could not find body field, but continuing...")
            
            screenshot_path = self.take_screenshot(session_id, "5_filled_email")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            # Step 6: Send email
            logger.info("Step 6: Sending email")
            send_button = None
            send_selectors = [
                "div[role='button'][data-tooltip*='Send']",
                "div[role='button'][aria-label*='Send']",
                "div[data-tooltip*='Send']",
                "div[aria-label*='Send']",
                "div[role='button'][title*='Send']"
            ]
            
            for selector in send_selectors:
                send_button = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=3)
                if send_button:
                    logger.info(f"Found send button with selector: {selector}")
                    break
            
            if not send_button:
                # Try XPath selectors as fallback
                xpath_selectors = [
                    "//div[contains(text(), 'Send')]",
                    "//div[@role='button' and contains(text(), 'Send')]",
                    "//div[contains(@aria-label, 'Send')]",
                    "//div[contains(@data-tooltip, 'Send')]",
                    "//span[contains(text(), 'Send')]",
                    "//button[contains(text(), 'Send')]"
                ]
                for xpath in xpath_selectors:
                    send_button = self.wait_for_element(By.XPATH, xpath, timeout=3)
                    if send_button:
                        logger.info(f"Found send button with XPath: {xpath}")
                        break
            
            if send_button:
                send_button.click()
                time.sleep(3)
                logger.info("Email sent successfully!")
            else:
                raise Exception("Could not find Send button")
            
            screenshot_path = self.take_screenshot(session_id, "6_sent")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            return {
                "status": "success",
                "message": "Email sent successfully!",
                "screenshots": screenshots,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Email automation failed: {e}")
            
            # Take error screenshot
            error_screenshot = self.take_screenshot(session_id, "error")
            if error_screenshot:
                screenshots.append(error_screenshot)
            
            return {
                "status": "error",
                "message": f"Email automation failed: {str(e)}",
                "screenshots": screenshots,
                "session_id": session_id
            }
        
        finally:
            # Clean up
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("Browser closed successfully")
                except Exception as e:
                    logger.error(f"Error closing browser: {e}")

def create_demo_screenshots(session_id):
    """Create demo screenshots for testing"""
    screenshots_dir = f"screenshots/{session_id}"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Create dummy screenshot files
    steps = [
        "1_gmail_login.png",
        "2_enter_email.png", 
        "3_enter_password.png",
        "4_compose.png",
        "5_filled_email.png",
        "6_sent.png"
    ]
    
    screenshots = []
    for step in steps:
        filepath = f"{screenshots_dir}/{step}"
        # Create a simple text file as placeholder
        with open(filepath, 'w') as f:
            f.write(f"Demo screenshot for {step}")
        screenshots.append(f"/screenshots/{session_id}/{step}")
    
    logger.info("Demo screenshots created successfully!")
    return screenshots 