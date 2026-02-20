from app import create_app, db
from models import User
import os

app = create_app()

def verify_pdf_generation():
    with app.app_context():
        # Get a user (create if needed, but we likely have one from previous tests)
        user = User.query.first()
        if not user:
            print("No user found. Please create a user first.")
            return

        with app.test_client() as client:
            # Simulate login
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['user_email'] = user.email
                sess['user_name'] = user.name

            # Request PDF
            print(f"Requesting PDF for user: {user.name}")
            response = client.get('/export/doctor_report')
            
            if response.status_code == 200:
                if response.headers['Content-Type'] == 'application/pdf':
                    print("SUCCESS: PDF generated successfully.")
                    print(f"Content-Length: {len(response.data)} bytes")
                    print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
                    
                    # Save for manual inspection if needed
                    output_path = "test_report.pdf"
                    with open(output_path, "wb") as f:
                        f.write(response.data)
                    print(f"Saved to {output_path}")
                else:
                    print(f"FAILED: Incorrect Content-Type: {response.headers['Content-Type']}")
            else:
                print(f"FAILED: Status Code {response.status_code}")
                print(response.data.decode('utf-8'))

if __name__ == "__main__":
    verify_pdf_generation()
