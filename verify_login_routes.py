
import requests

def test_routes():
    print("Testing Route Protection...")
    
    # 1. Dashboard (Protected) -> Should redirect (302) or return 401/403 if configured, or redirect to Login (200 OK after follow redirect if default requests)
    # Using allow_redirects=False to see the 302
    try:
        r_dashboard = requests.get("http://127.0.0.1:5000/dashboard", allow_redirects=False)
        print(f"Dashboard Status: {r_dashboard.status_code}")
        
        if r_dashboard.status_code == 302:
            print("✅ Dashboard is protected (Redirect found).")
            if "/login" in r_dashboard.headers.get("Location", ""):
                 print("✅ Redirects to /login.")
            else:
                 print(f"⚠️ Redirects to: {r_dashboard.headers.get('Location')}")
        else:
            print(f"❌ Dashboard is NOT protected (Status: {r_dashboard.status_code})")

    except Exception as e:
        print(f"Error testing dashboard: {e}")

    # 2. Home (Public) -> Should return 200 OK
    try:
        r_home = requests.get("http://127.0.0.1:5000/")
        print(f"Home Status: {r_home.status_code}")
        
        if r_home.status_code == 200:
            print("✅ Home is accessible.")
        else:
            print(f"❌ Home is NOT accessible (Status: {r_home.status_code})")
            
    except Exception as e:
        print(f"Error testing home: {e}")

    # 3. Login (Public) -> Should return 200 OK
    try:
        r_login = requests.get("http://127.0.0.1:5000/login")
        print(f"Login Status: {r_login.status_code}")
        
        if r_login.status_code == 200:
            print("✅ Login is accessible.")
        else:
            print(f"❌ Login is NOT accessible (Status: {r_login.status_code})")

    except Exception as e:
        print(f"Error testing login: {e}")

if __name__ == "__main__":
    test_routes()
