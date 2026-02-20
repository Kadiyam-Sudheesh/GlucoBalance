
from app import create_app, db
from models import User, Medication

def verify_crud():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db" 
    
    with app.app_context():
        db.create_all()
        
        # Create Dummy User
        if not User.query.filter_by(email="test@example.com").first():
            user = User(name="Test User", email="test@example.com", phone="1234567890", password="password")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            user_email = user.email
        else:
            user = User.query.filter_by(email="test@example.com").first()
            user_id = user.id
            user_email = user.email

        # Explicitly remove session to start fresh for client interactions if needed
        db.session.remove() 
        
        client = app.test_client()
        
        # Login
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["user_email"] = user_email
            
        print("1. Adding Medication...")
        resp = client.post("/medications", data={
            "name": "Test Med",
            "dosage": "100mg",
            "frequency": "Once Daily",
            "notes": "Original Note"
        }, follow_redirects=True)
        db.session.remove() # Clear session before querying
        med = Medication.query.filter_by(name="Test Med").first()
        if med:
            print(f"✅ Medication Added: {med.name} - {med.dosage}")
            med_id = med.id
        else:
            print("❌ Failed to add medication")
            return

        db.session.remove() # Clear session

        print("\n2. Editing Medication...")
        resp = client.post(f"/medications/edit/{med_id}", data={
            "name": "Test Med Updated",
            "dosage": "200mg",
            "frequency": "Twice Daily",
            "notes": "Updated Note"
        }, follow_redirects=True)
        
        db.session.remove() # Clear session
        
        # Re-query
        med = Medication.query.get(med_id)
        if med and med.name == "Test Med Updated" and med.dosage == "200mg":
            print(f"✅ Medication Updated: {med.name} - {med.dosage}")
        else:
            print(f"❌ Failed to update medication.")

        db.session.remove() # Clear session

        print("\n3. Deleting Medication...")
        resp = client.post(f"/medications/delete/{med_id}", follow_redirects=True)
        
        db.session.remove() # Clear session
        
        med_check = Medication.query.get(med_id)
        if not med_check:
            print("✅ Medication Deleted")
        else:
            print("❌ Failed to delete medication")
            
        # Cleanup
        # db.drop_all() # Optional

if __name__ == "__main__":
    verify_crud()
