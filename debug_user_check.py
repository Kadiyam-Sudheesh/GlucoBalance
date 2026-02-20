from app import create_app, db
from models import User

app = create_app()

def list_users():
    with app.app_context():
        print("--- All Users in Database ---")
        users = User.query.all()
        for u in users:
            print(f"ID: {u.id} | Name: {u.name} | Email: '{u.email}' | Phone: '{u.phone}' | Password: '{u.password}'")

if __name__ == "__main__":
    list_users()
