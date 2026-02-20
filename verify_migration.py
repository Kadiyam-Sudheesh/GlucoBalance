import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_full_flow():
    session = requests.Session()
    
    # 1. Signup
    print("--- Testing Signup ---")
    signup_url = f"{BASE_URL}/signup"
    user_data = {
        "name": "Test User DB",
        "email": "db_test@example.com",
        "phone": "9876543210",
        "country_code": "+1",
        "password": "password123",
        "confirm_password": "password123",
        "terms": "on"
    }
    response = session.post(signup_url, data=user_data, allow_redirects=True)
    print(f"Signup Status: {response.status_code}")
    if response.status_code == 200 and "/analyze" in response.url:
        print("SUCCESS: Signup redirect to /analyze")
    else:
        print(f"FAILURE: Signup failed. URL: {response.url}")
        print(response.text[:500])
        return

    # 2. Submit Report (Analyze)
    print("\n--- Testing Report Submission ---")
    analyze_url = f"{BASE_URL}/analyze"
    report_data = {
        "name": "Test User DB",
        "age": "30",
        "diabetes_type": "TYPE_2",
        "height_cm": "175",
        "weight_kg": "70",
        "test_date": "2026-02-12",
        "fbs": "110",
        "ppbs": "140",
        "hba1c": "6.5"
    }
    response = session.post(analyze_url, data=report_data, allow_redirects=True)
    print(f"Report Submission Status: {response.status_code}")
    if response.status_code == 200 and "Your Personalized Health Analysis" in response.text:
         print("SUCCESS: Report submitted and analysis generated.")
    else:
         print("FAILURE: Report submission failed.")
         print(response.text[:500])

    # 3. Dashboard (Verify persistence)
    print("\n--- Testing Dashboard (Persistence) ---")
    dashboard_url = f"{BASE_URL}/dashboard"
    response = session.get(dashboard_url)
    print(f"Dashboard Status: {response.status_code}")
    if response.status_code == 200:
        if "110" in response.text and "140" in response.text: # Check for FBS/PPBS values
            print("SUCCESS: Data persisted and visible on dashboard.")
        else:
            print("FAILURE: Data not found on dashboard.")
    else:
        print("FAILURE: Could not access dashboard.")

    # 4. Login (New Session)
    print("\n--- Testing Login (New Session) ---")
    new_session = requests.Session()
    login_url = f"{BASE_URL}/login"
    login_data = {
        "email": "db_test@example.com",
        "password": "password123"
    }
    response = new_session.post(login_url, data=login_data, allow_redirects=True)
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200 and "/analyze" in response.url:
        print("SUCCESS: Login redirect to /analyze")
    else:
        print(f"FAILURE: Login failed.")

if __name__ == "__main__":
    try:
        # Wait a bit for server to start if run immediately after
        time.sleep(2) 
        test_full_flow()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running.")
