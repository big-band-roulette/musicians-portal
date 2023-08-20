from models import Audition, AuditionUserLink, Event, Instrument,Musician,Singer,Arranger
from flask_security import hash_password
import datetime

def commitData(session,className,data):
    # Use bulk_insert_mappings to efficiently insert multiple rows at once
    session.bulk_insert_mappings(className, data)
    session.commit()

def insert_instruments(db_session):
            # Add the data for a big band
        data = [
            ("Trombone",1,1,1),
            ("Trombone",2,1,0),
            ("Trombone",3,0,0),
            ("Bass Trombone",4,0,0),
            ("Trumpet",1,1,1),
            ("Trumpet",2,1,0),
            ("Trumpet",3,0,0),
            ("Trumpet",4,0,0),
            ("Alto",1,1,0),
            ("Alto",2,0,0),
            ("Tenor",1,1,0),
            ("Tenor",2,0,0),
            ("Bari",1,0,0),
            ("Bass",1,0,0),
            ("Guitar",1,1,0),
            ("Piano",1,1,0),
            ("Drums",1,1,0),
            ("Percussion",1,0,0),
            ("Vocals",1,1,0)
        ]
        mapped_data = [{ "name": instrument,
                        "sectionPosition": position,
                        "takesSolos": solos,
                        "highRange": high_range } 
                        for instrument, position, solos, high_range in data]
        commitData(db_session,Instrument,mapped_data)

def insert_audition(db_session):
    data = ["Drums","Trumpet","Saxophone"]
    mapped_data = [{"name": name} for name in data]
    commitData(db_session,Audition,mapped_data)


def insert_gig(db_session):
    data = [("Night at the Movies",
    "Honestly I have no clue, but I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2001,10,1),
    "Cambridge!" 
    ),
    ("John's May Ball",
    "Here's another description I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2001,10,1),
    "Cambridge!" 
    ),
    ("Robinson May Ball",
    "Honestly I have no clue, but I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2001,10,1),
    "Cambridge!" 
    ),
    ("RoadTrippin!",
    "Honestly I have no clue, but I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2023,2,1),
    "Cambridge!" 
    ),
    ("Swinging 60's",
    "Honestly I have no clue, but I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2000,5,1),
    "Cambridge!" 
    )]
    mapped_data = [
        {"name": name,
         "description": description,
         "date": date,
         "location": location
        } for name, description, date, location in data]

    commitData(db_session,Event,mapped_data)


def add_simulated_data(app,db_session):
    
    # Create users and roles to test with
    app.security.datastore.find_or_create_role(
        name="user", permissions={"user-read", "user-write"}
    )
    db_session.commit()
    app.security.datastore.find_or_create_role(
        name="auditioned", permissions={"user-read", "user-write"}
    )
    db_session.commit()
    app.security.datastore.find_or_create_role(
        name="admin", permissions={"user-read", "user-write"}
    )
    db_session.commit()

    musician = Musician()
    singer = Singer(vocal_range='Alto', singer_audition_video_url='...')
    arranger = Arranger(arranger_audition_video_url='...')
    if not app.security.datastore.find_user(email="test@me.com"):
        app.security.datastore.create_user(email="test@me.com",
        password=hash_password("password"), roles=["user","admin"],band_roles=[arranger])
    db_session.commit()

    if not app.security.datastore.find_user(email="2@me.com"):
        app.security.datastore.create_user(email="2@me.com",
        password=hash_password("2"), roles=["user","auditioned"],band_roles=[musician,singer])
    db_session.commit()


    insert_instruments(db_session)
    insert_audition(db_session)
    insert_gig(db_session)

    signup = AuditionUserLink(user_id = 1, audition_id = 1)
    db_session.add(signup)
    db_session.commit()