# init_db.py
from app import app
from database import init_db, db_session
import datetime

from models import AuditionSlot, AuditionSession

MD = "Tim Hargreaves"
START_TIME = datetime.datetime(2021, 9, 14, 14, 0, 0)
END_TIME = datetime.datetime(2021, 9, 14, 18, 0, 0)
LOCATION = "Band Room, St John's College"
DIRECTIONS = "Wait at the Cripps porter's lodge (https://maps.app.goo.gl/2vF411Lt65LvtCj66), which you can access via Northampton Street or by walking through the college. We will come up from the band room to collect you just before your audition slot."

SLOT_LENGTH = datetime.timedelta(minutes=30)
SLOT_OFFSET = datetime.timedelta(minutes=40)

def commitData(session,className,data):
    # Use bulk_insert_mappings to efficiently insert multiple rows at once
    session.bulk_insert_mappings(className, data)
    session.commit()

if __name__ == "__main__":
  with app.app_context():
    init_db(app)

    # Create audition sessions
    mapped_data = [
        {
            "musical_director": MD,
            "start_time": START_TIME,
            "end_time": END_TIME,
            "location": LOCATION,
        }
    ]
    commitData(db_session, AuditionSession, mapped_data)

    # Fill audition slots
    audition_sessions = db_session.query(AuditionSession).all()
    for audition_session in audition_sessions:
        start_time = audition_session.start_time
        end_time = start_time + SLOT_LENGTH
        while end_time <= audition_session.end_time:
            audition_session.audition_slots.append(
                AuditionSlot(start_time=start_time, end_time=end_time)
            )
            start_time += SLOT_OFFSET
            end_time += SLOT_LENGTH
    db_session.commit()
