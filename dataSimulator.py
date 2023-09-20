from models import Audition, Drums, Event, Guitar, \
    Musician, Percussion, Piano, Saxophone,Singer,Arranger, Trombone
from flask_security import hash_password
import datetime

def commitData(session,className,data):
    # Use bulk_insert_mappings to efficiently insert multiple rows at once
    session.bulk_insert_mappings(className, data)
    session.commit()

def insert_audition(db_session):
    data = [
         (datetime.datetime(2020,10,1,19,45,0),'London'),
         (datetime.datetime(2023,8,1,14,45,0),'Dubai'),
         (datetime.datetime(2023,10,1,4,45,0),'West Road Concert Hall'),
         (datetime.datetime(2023,10,1,10,45,0),'West Road Concert Hall'),
         (datetime.datetime(2023,10,1,11,45,0),'West Road Concert Hall'),
         (datetime.datetime(2023,10,1,19,55,0),'West Road Concert Hall'),
         (datetime.datetime(2023,10,1,18,45,0),'West Road Concert Hall'),
         (datetime.datetime(2023,10,1,20,45,0),'West Road Concert Hall'),
         (datetime.datetime(2023,10,1,16,45,0),'West Road Concert Hall'),
         ]
    mapped_data = [{"datetime": date, "details": "TBD", "location": location} for date, location in data]
    commitData(db_session,Audition,mapped_data)


def insert_gig(db_session):
    data = [("West Road Concert Hall",
    "This one was a concert so memorable I have no more details about itup with on the spot and so there's probably a bug in it somewhere This one was a concert so memorable I have no more details about itup with on the spot and so there's probably a bug in it somewhere This one was a concert so memorable I have no more details about itup with on the spot and so there's probably a bug in it somewhere This one was a concert so memorable I have no more details about itup with on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2022,10,1,19,45,0),
    "Cambridge!" 
    ),
    ("Night at the Movies",
        "This one was a concert so memorable I have no more details about itup with on the spot and so there's probably a bug in it somewhere This one was a concert so memorable I have no more details about itup with on the spot and so there's probably a bug in it somewhere This one was a concert so memorable I have no more details about itup with on the spot and so there's probably a bug in it somewhere This one was a concert so memorable I have no more details about itup with on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2023,9,1,19,45,0),
    "Cambridge!" 
    ),
    ("John's May Ball",
    "Here's another description I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2023,10,1,19,45,0),
    "Cambridge!" 
    ),
    ("Robinson May Ball",
    "Honestly I have no clue, but I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2023,11,1,19,45,0),
    "Cambridge!" 
    ),
    ("RoadTrippin!",
    "Honestly I have no clue, but I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2023,12,1,19,45,0),
    "Cambridge!" 
    ),
    ("Swinging 60's",
    "Honestly I have no clue, but I came up wi\
    th on the spot and so there's probably a bug in it somewhere",
    datetime.datetime(2024,1,1,19,45,0),
    "Cambridge!" 
    )]
    mapped_data = [
        {"name": name,
         "description": description,
         "datetime": date,
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


    insert_audition(db_session)
    insert_gig(db_session)


    instruments = [
        Trombone(user_id=1, trombone_1=True, takes_solos=True),
        Saxophone(user_id=1, alto_1=True, takes_solos=True),
        Saxophone(user_id=2, alto_1=True, takes_solos=False),
        Guitar(user_id=2, takes_solos=True),
        Drums(user_id=2, takes_solos=False),
        Piano(user_id=2, takes_solos=True),
        Percussion(user_id=2, takes_solos=False),
        Guitar(user_id=1, takes_solos=True),
        Drums(user_id=1, takes_solos=False,bongos=True),
        Piano(user_id=1, takes_solos=True),
        Percussion(user_id=1, takes_solos=False,bongos=True),
    ]
    for instrument in instruments:
        db_session.add(instrument)
        db_session.commit()