from app import create_app, db
from models import User, FoodLog
import datetime

def verify_food_logger():
    app = create_app()
    with app.app_context():
        print("Verifying Food Logger...")
        
        # 1. Setup User
        user = User.query.filter_by(email="test_food@example.com").first()
        if not user:
            user = User(name="Food Tester", email="test_food@example.com", password="hash", age=40, diabetes_type="Type_2")
            db.session.add(user)
            db.session.commit()
            print(f"Created test user: {user.id}")
        else:
            print(f"Using existing user: {user.id}")

        # 2. Log a Meal
        # Clear existing logs for test user
        FoodLog.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        print("Logging a Green Meal (Salad)...")
        log1 = FoodLog(
            user_id=user.id,
            name="Grilled Chicken Salad",
            category="Lunch",
            glycemic_impact="LOW_GREEN",
            portion="Medium",
            notes="Healthy choice"
        )
        db.session.add(log1)
        
        print("Logging a Red Meal (Cake)...")
        log2 = FoodLog(
            user_id=user.id,
            name="Chocolate Cake",
            category="Snack",
            glycemic_impact="HIGH_RED",
            portion="Small",
            notes="Birthday party"
        )
        db.session.add(log2)
        db.session.commit()

        # 3. Verify Logs
        logs = FoodLog.query.filter_by(user_id=user.id).order_by(FoodLog.timestamp.desc()).all()
        
        if len(logs) == 2:
            print(f"✅ Successfully retrieved {len(logs)} logs.")
            print(f"Log 1: {logs[0].name} ({logs[0].glycemic_impact})")
            print(f"Log 2: {logs[1].name} ({logs[1].glycemic_impact})")
        else:
            print(f"❌ Failed to retrieve logs. Found {len(logs)}")

        # Cleanup
        # db.session.delete(user)
        db.session.commit()
        print("Verification Complete")

if __name__ == "__main__":
    verify_food_logger()
