from app import create_app, db
from models import User, EmergencyContact, HypoEvent
import datetime

def verify_emergency_feature():
    app = create_app()
    with app.app_context():
        print("Verifying Emergency Feature...")
        
        # 1. Setup User
        user = User.query.filter_by(email="test_emergency@example.com").first()
        if not user:
            user = User(name="Emergency Tester", email="test_emergency@example.com", password="hash", age=30, diabetes_type="Type_1")
            db.session.add(user)
            db.session.commit()
            print(f"Created test user: {user.id}")
        else:
            print(f"Using existing user: {user.id}")

        # 2. Test Contact Management
        # Clear existing
        EmergencyContact.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # Add Contact
        contact = EmergencyContact(user_id=user.id, name="Mom", phone="555-1234")
        db.session.add(contact)
        db.session.commit()
        
        retrieved_contact = EmergencyContact.query.filter_by(user_id=user.id).first()
        if retrieved_contact and retrieved_contact.name == "Mom":
            print("✅ Emergency Contact Added")
        else:
            print("❌ Contact Verification Failed")

        # 3. Test Hypo Event Logging
        # Start Event
        event = HypoEvent(user_id=user.id, status="STARTED", notes="Test Event")
        db.session.add(event)
        db.session.commit()
        event_id = event.id
        print(f"Started Event ID: {event_id}")

        # Resolve Event
        event_to_resolve = HypoEvent.query.get(event_id)
        event_to_resolve.status = "RESOLVED"
        event_to_resolve.notes += " - Resolved"
        db.session.commit()

        final_event = HypoEvent.query.get(event_id)
        if final_event.status == "RESOLVED":
            print("✅ Hypo Event Resolved")
        else:
            print("❌ Event Resolution Failed")

        # Cleanup
        db.session.delete(retrieved_contact)
        db.session.delete(final_event)
        # db.session.delete(user) # Keep user for potential manual testing or other tests
        db.session.commit()
        print("Cleanup Complete")

if __name__ == "__main__":
    verify_emergency_feature()
