import requests

def test_login_and_render():
    base_url = "http://127.0.0.1:5000"
    login_url = f"{base_url}/login"
    
    session = requests.Session()
    session.get(login_url) # Init session/cookies
    
    credentials = {
        "email": "sudheeshy999@gmail.com",
        "password": "Sudheesh@5699"
    }
    
    print("\nPOST /login (following redirects)")
    response = session.post(login_url, data=credentials, allow_redirects=True)
    
    print(f"Final Status: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    if response.status_code == 200 and "/analyze" in response.url:
        print("SUCCESS: Landed on /analyze")
        if "New Health Analysis" in response.text:
            print("SUCCESS: 'New Health Analysis' text found in response.")
        else:
            print("WARNING: 'New Health Analysis' text NOT found. Page content might be unexpected.")
            print(response.text[:500])
    else:
        print(f"FAILURE: Did not land on /analyze. URL: {response.url}, Status: {response.status_code}")
        print(response.text[:500])

if __name__ == "__main__":
    try:
        test_login_and_render()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
