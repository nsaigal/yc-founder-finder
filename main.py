import os
import json
import shutil
import argparse
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from vision import Vision

# Load environment variables from a .env file
load_dotenv()

def setup_driver():
    # Set up and configure the Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode
    
    # Try to find Chrome in common locations
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
        "/usr/bin/google-chrome",  # Linux
        "/usr/bin/chromium-browser",  # Linux alternative
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",  # Windows 32-bit
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_options.binary_location = path
            chrome_found = True
            break
    
    if not chrome_found:
        print("⚠️  Chrome not found in common locations. Trying to use system default...")
        print("💡 If this fails, please install Chrome or specify the path manually.")
    
    try:
        # Try using Chrome's built-in ChromeDriver first (most reliable for version matching)
        print("🔍 Trying Chrome's built-in ChromeDriver...")
        return webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"❌ Failed with Chrome's built-in ChromeDriver: {e}")
        try:
            # Try using the system ChromeDriver
            service = Service("/opt/homebrew/bin/chromedriver")
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e2:
            print(f"❌ Failed with system ChromeDriver: {e2}")
            try:
                # Fallback to webdriver-manager with specific version handling
                print("🔍 Trying webdriver-manager...")
                try:
                    service = Service(ChromeDriverManager().install())
                    return webdriver.Chrome(service=service, options=chrome_options)
                except ValueError as ve:
                    if "There is no such driver" in str(ve):
                        print("⚠️  ChromeDriver version mismatch detected. Trying with latest available version...")
                        # Try with a more recent stable version that should work
                        try:
                            service = Service(ChromeDriverManager(version="131.0.6778.87").install())
                            return webdriver.Chrome(service=service, options=chrome_options)
                        except:
                            # Try with an even more recent version
                            service = Service(ChromeDriverManager(version="131.0.6778.108").install())
                            return webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        raise
            except Exception as e3:
                print(f"❌ Failed to start Chrome: {e3}")
                print("🔧 Please ensure Chrome is installed and try again.")
                print("📥 Download Chrome from: https://www.google.com/chrome/")
                print("💡 Try running: brew install --cask google-chrome")
                print("💡 Or try updating ChromeDriver: brew upgrade chromedriver")
                print("💡 Or try: brew install chromedriver")
                print("💡 Alternative: Try downgrading Chrome to a stable version")
                raise

def login(driver, username, password):
    # Log in to the YC Startup School website
    print("🔐 Attempting to log in...")
    
    try:
        # Wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Try different possible selectors for username field
        username_selectors = [
            (By.ID, "ycid-input"),
            (By.NAME, "email"),
            (By.NAME, "username"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[placeholder*='email']"),
            (By.CSS_SELECTOR, "input[placeholder*='Email']")
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                username_field = WebDriverWait(driver, 3).until(EC.presence_of_element_located(selector))
                print(f"✅ Found username field with selector: {selector}")
                break
            except:
                continue
        
        if not username_field:
            print("❌ Could not find username field. Taking screenshot for debugging...")
            driver.save_screenshot("login_page_debug.png")
            raise Exception("Username field not found")
        
        username_field.clear()
        username_field.send_keys(username)
        print("✅ Username entered")
        
        # Try different possible selectors for password field
        password_selectors = [
            (By.ID, "password-input"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']")
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(*selector)
                print(f"✅ Found password field with selector: {selector}")
                break
            except:
                continue
        
        if not password_field:
            print("❌ Could not find password field")
            raise Exception("Password field not found")
        
        password_field.clear()
        password_field.send_keys(password)
        print("✅ Password entered")
        
        # Try different possible selectors for login button
        login_button_selectors = [
            (By.CLASS_NAME, "sign-in-button"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Sign In')]"),
            (By.XPATH, "//button[contains(text(), 'Login')]"),
            (By.XPATH, "//input[@value='Sign In']"),
            (By.XPATH, "//input[@value='Login']")
        ]
        
        login_button = None
        for selector in login_button_selectors:
            try:
                login_button = driver.find_element(*selector)
                print(f"✅ Found login button with selector: {selector}")
                break
            except:
                continue
        
        if not login_button:
            print("❌ Could not find login button")
            raise Exception("Login button not found")
        
        login_button.click()
        print("✅ Login button clicked")
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        print("📸 Taking screenshot for debugging...")
        driver.save_screenshot("login_error_debug.png")
        raise

def evaluate_profile(vision_model, ss_path):
    # Evaluate a profile using the vision model
    prompt = "Evaluate the profile and tell me if they are a good fit for me."
    try:
        response = vision_model.generate_response(prompt, [ss_path])
        print(response)
        return response
    except Exception as e:
        print(f"❌ AI evaluation failed: {e}")
        print("🔄 Defaulting to skip this profile...")
        # Return a default "skip" response
        return {
            "is_good_fit": False,
            "personalized_intro_message": ""
        }

def perform_action(driver, action_type):
    # Perform a specific action on the webpage
    try:
        if action_type == 'save':
            element = driver.find_element(By.XPATH, '//div[contains(text(), "Save to favorites")]')
        elif action_type == 'send':
            element = driver.find_element(By.XPATH, '//button[contains(text(), "Invite to connect")]')
        elif action_type == 'next':
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "See next profile")]')))
        elif action_type == 'skip':
            element = driver.find_element(By.XPATH, '//button[contains(text(), "Skip for now")]')
        
        # Wait until the element is clickable and then perform the action
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
        ActionChains(driver).move_to_element(element).click().perform()
        print(f"Clicked on {action_type} button")
    except Exception as e:
        print(f"Failed to find or click {action_type} button: {e}")
        raise e

def write_message(driver, message):
    # Write a message in the textarea on the webpage
    try:
        textarea = driver.find_element(By.TAG_NAME, "textarea")
        textarea.send_keys(message)
    except Exception as e:
        print(f"Failed to find or write message: {e}")
        raise e

def start(url, username, password, vision_model):
    driver = setup_driver()
    print(f"🌐 Navigating to: {url}")
    driver.get(url)
    
    # Debug: Print current page info
    print(f"📄 Current URL: {driver.current_url}")
    print(f"📄 Page title: {driver.title}")
    
    login(driver, username, password)
    
    # Wait until the page content is loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "page-content")))
    print('Logged in')
    
    viewed_profiles = set()
    while len(viewed_profiles) < 10:
        url = driver.current_url
        viewed_profiles.add(url)

        # Zoom out to capture the entire profile
        driver.execute_script("document.body.style.zoom='45%'")

        # Take a screenshot of the current page
        ss_path = f"{url.split('/')[-1]}.png"
        driver.save_screenshot(ss_path)

        # Evaluate the profile using the vision model
        evaluation = evaluate_profile(vision_model, ss_path)

        if evaluation.get('is_good_fit', False):
            try:
                if evaluation.get('personalized_intro_message', '') != '':
                    # Save the profile screenshot
                    os.makedirs('saved_profiles', exist_ok=True)
                    saved_ss_path = os.path.join('saved_profiles', ss_path)
                    shutil.copy(ss_path, saved_ss_path)

                    # Write a personalized message to the candidate
                    write_message(driver, evaluation['personalized_intro_message'])
                    perform_action(driver, 'send')
                else:
                    # Save profile to favorites
                    perform_action(driver, 'save')
            except Exception:
                perform_action(driver, 'skip')
        else:
            perform_action(driver, 'skip')
        
        # Wait for the next profile to load
        WebDriverWait(driver, 10).until(
            EC.url_changes(url)
        )
        
        # Wait for the page content to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-content"))
        )

        # Remove the screenshot after processing
        os.remove(ss_path)

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find YC co-founder matches using vision models")
    parser.add_argument("--provider", choices=["openai", "anthropic", "ollama"], 
                       default="openai", help="Vision model provider to use")
    parser.add_argument("--model", help="Specific model to use (optional)")
    args = parser.parse_args()

    url = "https://www.startupschool.org/cofounder-matching/candidate/next"
    username = os.getenv("YC_USERNAME")
    password = os.getenv("YC_PASSWORD")
    
    # Check if credentials are provided
    if not username or not password:
        print("❌ Missing credentials!")
        print("🔧 Please set the following environment variables:")
        print("   YC_USERNAME=your_username")
        print("   YC_PASSWORD=your_password")
        print("💡 You can create a .env file in the project directory with:")
        print("   YC_USERNAME=your_username_here")
        print("   YC_PASSWORD=your_password_here")
        exit(1)
    
    # Create vision model using the consolidated interface
    vision_model = Vision(provider=args.provider, model=args.model)
    
    print(f"Using {args.provider} model: {vision_model.model}")
    
    start(url, username, password, vision_model)