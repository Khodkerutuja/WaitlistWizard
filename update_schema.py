from app import app, db

def update_schema():
    with app.app_context():
        print("Updating database schema...")
        db.create_all()
        print("Database schema updated!")

if __name__ == "__main__":
    update_schema()