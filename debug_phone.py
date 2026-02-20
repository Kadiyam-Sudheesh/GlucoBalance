from app import create_app, db
from models import User

app = create_app()

def debug_phone_login():
    with app.app_context():
        # 1. List all users and their stored phone numbers to see format
        print("--- Existing Users ---")
        users = User.query.all()
        for u in users:
            print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}, Phone: '{u.phone}'")

        # 2. Simulate Login Logic
        print("\n--- Simulating Phone Logic ---")
        test_phone_input = "9876543210" # Example from previous verification
        test_country_code = "+1" 
        
        full_phone = f"{test_country_code}{test_phone_input}"
        print(f"Searching for phone: '{full_phone}'")
        
        user = User.query.filter_by(phone=full_phone).first()
        
        if user:
            print(f"SUCCESS: Found user {user.name} with phone {full_phone}")
        else:
            print(f"FAILURE: User not found with phone {full_phone}")
            
        # 3. Test with +91 (common issue if user forgets country code in signup or login)
        test_country_code_2 = "+91"
        full_phone_2 = f"{test_country_code_2}{test_phone_input}"
        print(f"\nSearching for phone: '{full_phone_2}'")
        user_2 = User.query.filter_by(phone=full_phone_2).first()
        if user_2:
            print(f"SUCCESS: Found user {user_2.name} with phone {full_phone_2}")

if __name__ == "__main__":
    debug_phone_login()
