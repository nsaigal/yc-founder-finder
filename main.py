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

from vision.gpt4v import GPT4V
from vision.llava import LLaVA

# Load environment variables from a .env file
load_dotenv()

def setup_driver():
    # Set up and configure the Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def login(driver, username, password):
    # Log in to the YC Startup School website
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ycid-input")))
    username_field.send_keys(username)
    
    password_field = driver.find_element(By.ID, "password-input")
    password_field.send_keys(password)
    
    login_button = driver.find_element(By.CLASS_NAME, "sign-in-button")
    login_button.click()

def evaluate_profile(vision_model, ss_path):
    # Evaluate a profile using the vision model
    prompt = "Evaluate the profile and tell me if they are a good fit for me."
    response = vision_model.generate_response(prompt, [ss_path])
    print(response)
    return response

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
    driver.get(url)
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
    parser.add_argument("--local", action="store_true", help="Use local LLaVA model instead of remote GPT-4V")
    args = parser.parse_args()

    url = "https://www.startupschool.org/cofounder-matching/candidate/next"
    username = os.getenv("YC_USERNAME")
    password = os.getenv("YC_PASSWORD")
    
    # Choose the vision model based on the argument
    vision_model = LLaVA(host="http://localhost:11434") if args.local else GPT4V()
    
    if args.local and not vision_model.ping():
        print("LLaVA model not running. Please start LLaVA locally.")
        exit(1)
    
    print(f"Using {'local LLaVA' if args.local else 'OpenAI GPT-4V'} model")
    
    start(url, username, password, vision_model)