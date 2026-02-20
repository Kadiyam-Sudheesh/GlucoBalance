from app import create_app, db
from models import User, Medication, MedicationLog
import datetime

app = create_app()

def verify_medication_feature():
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        print("Database tables checked/created.")

        # Create a dummy user for testing
        test_email = "test_med@example.com"
        user = User.query.filter_by(email=test_email).first()
        if not user:
            user = User(name="Test User", email=test_email, password="password", phone="1234567890")
            db.session.add(user)
            db.session.commit()
            print(f"Created test user: {user.email}")
        else:
            print(f"Using existing test user: {user.email}")

        # Add a medication
        med = Medication(
            user_id=user.id,
            name="Test Med 500mg",
            dosage="500mg",
            frequency="Daily",
            notes="Take with water"
        )
        db.session.add(med)
        db.session.commit()
        print(f"Added medication: {med.name} (ID: {med.id})")

        # Log it
        log = MedicationLog(
            medication_id=med.id,
            status="TAKEN"
        )
        db.session.add(log)
        db.session.commit()
        print(f"Logged medication usage for ID {med.id}")

        # Verify
        saved_med = Medication.query.get(med.id)
        saved_log = MedicationLog.query.filter_by(medication_id=med.id).first()
        
        if saved_med and saved_log:
            print("VERIFICATION SUCCESS: Medication and Log retrieved successfully.")
            
            # Cleanup
            db.session.delete(saved_log)
            db.session.delete(saved_med)
            # db.session.delete(user) # Keep user for now or delete
            db.session.commit()
            print("Cleanup complete.")
        else:
            print("VERIFICATION FAILED: Could not retrieve saved data.")

if __name__ == "__main__":
    verify_medication_feature()
