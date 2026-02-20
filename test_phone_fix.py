import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_robust_phone_login():
    session = requests.Session()
    session.get(f"{BASE_URL}/login") # Init cookies
    
    # 1. Create a User with known phone format
    print("\n--- Creating Test User for Phone ---")
    signup_url = f"{BASE_URL}/signup"
    user_data = {
        "name": "Phone Test User",
        "email": "phone_test@example.com",
        "phone": "5551234567",
        "country_code": "+1", # Stored as +15551234567
        "password": "password123",
        "confirm_password": "password123",
        "terms": "on"
    }
    # Clean up if exists (optional, or just ignore error)
    
    response = session.post(signup_url, data=user_data, allow_redirects=True)
    if response.status_code == 200 and ("/analyze" in response.url or "Email already registered" in response.text):
        print("SUCCESS: User created/exists.")
    else:
        print(f"FAILURE: User creation failed. {response.status_code}")
        print(response.text[:200])
        
    login_url = f"{BASE_URL}/login"

    # Test Case 1: Standard Login (Correct Dropdown + Number)
    print("\n--- Test Case 1: Standard Login (+1, 5551234567) ---")
    session = requests.Session() # New session
    login_data = {
        "country_code": "+1",
        "phone": "5551234567",
        "password": "password123"
    }
    response = session.post(login_url, data=login_data, allow_redirects=True)
    if response.status_code == 200 and "/analyze" in response.url:
        print("SUCCESS: Standard login worked.")
    else:
        print(f"FAILURE: Standard login failed. URL: {response.url}")

    # Test Case 2: Full International Number in Input (Ignore Dropdown +1)
    print("\n--- Test Case 2: Full International Input (+15551234567) with Dropdown +1 ---")
    session = requests.Session()
    login_data = {
        "country_code": "+1", # Dropdown says +1
        "phone": "+15551234567", # Input says +1...
        "password": "password123"
    }
    # Expected: Backend sees input starts with +, ignores dropdown, uses input. Input matches stored.
    response = session.post(login_url, data=login_data, allow_redirects=True)
    if response.status_code == 200 and "/analyze" in response.url:
        print("SUCCESS: Full international input login worked.")
    else:
        print(f"FAILURE: Full international input login failed. URL: {response.url}")

    # Test Case 3: Spaces/Dashes in Input
    print("\n--- Test Case 3: Input with Spaces ( 555 123 4567 ) ---")
    session = requests.Session()
    login_data = {
        "country_code": "+1",
        "phone": " 555 123-4567 ",
        "password": "password123"
    }
    response = session.post(login_url, data=login_data, allow_redirects=True)
    if response.status_code == 200 and "/analyze" in response.url:
        print("SUCCESS: Spaced input login worked.")
    else:
        print(f"FAILURE: Spaced input login failed. URL: {response.url}")
        
    # Test Case 4: Wrong Dropdown but Correct Full Input
    print("\n--- Test Case 4: Wrong Dropdown (+91) but Full Input (+15551234567) ---")
    session = requests.Session()
    login_data = {
        "country_code": "+91", # Wrong country code selected
        "phone": "+15551234567", # Correct full number typed
        "password": "password123"
    }
    response = session.post(login_url, data=login_data, allow_redirects=True)
    if response.status_code == 200 and "/analyze" in response.url:
        print("SUCCESS: Wrong dropdown + full input login worked.")
    else:
        print(f"FAILURE: Wrong dropdown + full input login failed. URL: {response.url}")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_robust_phone_login()
    except Exception as e:
        print(f"Error: {e}")
