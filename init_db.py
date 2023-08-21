# init_db.py
from app import app
from database import init_db, db_session
from dataSimulator import add_simulated_data
from dotenv import load_dotenv

if __name__ == "__main__":
  load_dotenv()
  with app.app_context():
    init_db(app)
    add_simulated_data(app,db_session)