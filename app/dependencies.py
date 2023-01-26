from database import conn

def get_db():
    db = conn.SessionLocal()
    try:
        yield db
    finally:
        db.close()

