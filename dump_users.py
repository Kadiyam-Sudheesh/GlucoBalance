from app import create_app, db
from models import User
import sys

app = create_app()

def dump_users():
    with app.app_context():
        with open("clean_users.txt", "w", encoding="utf-8") as f:
            f.write("--- All Users in Database ---\n")
            users = User.query.all()
            for u in users:
                f.write(f"ID: {u.id} | Name: {u.name} | Email: '{u.email}' | Phone: '{u.phone}'\n")
            f.write("--- End of List ---\n")
        print("Dumped users to clean_users.txt")

if __name__ == "__main__":
    dump_users()
