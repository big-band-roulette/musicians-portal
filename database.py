from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dataSimulator import add_simulated_data
from models import Base
import os

# Database configuration
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD') 
db_name = os.environ.get('DB_NAME')
db_host = os.environ.get('DB_HOST')  # Usually 'localhost' or an IP address
print(db_user,db_password,db_name,db_host)
# Create the engine
engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}")

#engine = create_engine('sqlite:///database.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base.query = db_session.query_property()

def init_db(app):
    # # import all modules here that might define models so that
    # # they will be registered properly on the metadata.  Otherwise
    # # you will have to import them first before calling init_db()
    import models

    with db_session() as session:
        Base.metadata.drop_all(bind=engine)
        session.commit()
        Base.metadata.create_all(bind=engine)
        session.commit()
        add_simulated_data(app,session)
        session.commit()
    # except SQLAlchemyError as e:
    #     print("Error:", e)
    #     session.rollback()