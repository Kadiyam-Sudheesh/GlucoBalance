from app import create_app, db
from models import User, Report
from datetime import date, timedelta

def verify_hba1c():
    app = create_app()
    with app.app_context():
        print("Verifying HbA1c Estimator...")
        
        # 1. Setup User
        user = User.query.filter_by(email="test_hba1c@example.com").first()
        if not user:
            user = User(name="Hba1c Tester", email="test_hba1c@example.com", password="hash", age=45, diabetes_type="Type_2")
            db.session.add(user)
            db.session.commit()
        
        # 2. Clear Reports
        Report.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        # 3. Add Dummy Reports (Avg 150 mg/dL)
        # Formula: (150 + 46.7) / 28.7 = 6.85
        
        r1 = Report(user_id=user.id, fbs=150, ppbs=150, hba1c=6.5, test_date=date.today())
        r2 = Report(user_id=user.id, fbs=150, ppbs=150, hba1c=6.5, test_date=date.today() - timedelta(days=1))
        
        db.session.add(r1)
        db.session.add(r2)
        db.session.commit()
        
        # 4. Verify Calculation
        estimate = user.get_estimated_hba1c()
        print(f"Calculated Estimate: {estimate}%")
        
        if estimate == 6.9: # Rounding 6.853... to 6.9 or 6.8? Function uses round(x, 1). 6.85 -> 6.9 usually (round half to even mechanism in py3 might be 6.8 or 6.9 depending on float rep).
            # actually (150+46.7)/28.7 = 6.8536. round(6.8536, 1) = 6.9.
            print("✅ Estimate matches expected value (6.9%)")
        else:
            print(f"⚠️ Estimate mismatch. Expected ~6.9%")

        # Cleanup
        # db.session.delete(user)
        db.session.commit()

if __name__ == "__main__":
    verify_hba1c()
