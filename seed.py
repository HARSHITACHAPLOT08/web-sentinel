from database.db_manager import DBManager

def seed():
    db = DBManager()
    print("Seeding database...")
    try:
        db.add_website("Google", "https://www.google.com", 60)
        print("Added: Google")
        db.add_website("Example", "https://example.com", 120)
        print("Added: Example")
    except Exception as e:
        print(f"Error seeding: {e}")

if __name__ == "__main__":
    seed()
