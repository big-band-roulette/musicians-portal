from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import Base
import os

from dotenv import load_dotenv
load_dotenv()

# Database configuration
db_local = os.environ.get('DB_LOCAL')
db_user = os.environ.get('DB_USER')
db_password = '' if os.environ.get('DB_HOST') == 'localhost' else os.environ.get('DB_PASSWORD') 
db_name = os.environ.get('DB_NAME')
db_host = os.environ.get('DB_HOST')  # Usually 'localhost' or an IP address

# Create the engine
if db_local == 'yes':
    engine = create_engine(f"sqlite:///database.db", echo=False)
elif db_local == 'no':
    engine = create_engine(
        f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}",
        echo=False
    )
else:
    raise ValueError("DB_LOCAL must be 'yes' or 'no'")
    

#engine = create_engine('sqlite:///database.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                        autoflush=True,
                                        bind=engine))

Base.query = db_session.query_property()

def init_db(app):
    # # import all modules here that might define models so that
    # # they will be registered properly on the metadata.  Otherwise
    # # you will have to import them first before calling init_db()
    import models

    with db_session() as session:
        # NB: This Base is the same object as Models.Base
        Base.metadata.drop_all(bind=engine)
        session.commit()
        Base.metadata.create_all(bind=engine)
        session.commit()
    # except SQLAlchemyError as e:
    #     print("Error:", e)
    #     session.rollback()