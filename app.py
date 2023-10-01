from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, url_for, redirect,render_template, request, flash
from flask_cors import CORS
from flask_security import Security, roles_required,current_user, auth_required, \
     SQLAlchemySessionUserDatastore
from database import db_session
from models import * #! All models should be imported automatically, even if more are defined
from config import Config
from flask_mailman import Mail
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField
from flask_wtf.csrf import CSRFProtect
from collections import defaultdict
from sqlalchemy.exc import IntegrityError
from wtforms import BooleanField, StringField, SubmitField
from sqlalchemy.sql.sqltypes import Boolean,String

# Create app
app = Flask(__name__)
app.config.from_object(Config)
crsf = CSRFProtect(app)
CORS(app)
# class R(Request):
#     # Whitelist SRCF and/or custom domains to access the site via proxy.
#     trusted_hosts = {"bbr.soc.srcf.net","dev.bigbandroulette.com"}
# app.request_class = R

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
app.security = Security(app, user_datastore)

# mail setup
mail = Mail(app)

# confirmation for joining the event pool
class ConfirmationForm(FlaskForm):
    event_id = StringField('Event ID')
    submit = SubmitField('Submit')

# Views

@app.route("/auditions")
@auth_required()
def auditions():
    instruments = [instrument.__name__ for instrument in  Instrument.__subclasses__()]
    levels = [
        '1',
        '1–2',
        '2',
        '2–3',
        '3',
        '3–4',
        '4',
    ]

    audition_sessions = db_session.query(AuditionSession).all()
    sessions_slots = [len(session.audition_slots) for session in audition_sessions]
    sessions_remaining = [
        len([slot for slot in session.audition_slots if slot.user is None])
        for session in audition_sessions
    ]

    audition_sessions_with_availability = [
        (audition_session, session_slots, session_remaining)
        for audition_session, session_slots, session_remaining in zip(audition_sessions, sessions_slots, sessions_remaining)
    ]

    print(audition_sessions_with_availability)

    return render_template('auditions.html', 
                           audition_sessions_with_availability=audition_sessions_with_availability, 
                           instruments = instruments,
                           levels = levels,
                           )

@app.route('/toggle_notifications', methods=['POST'])
@auth_required()
def toggle_notifications():
    user = db_session.query(User).get(request.form['user_id'])
    notification_type = request.form['form_type']
    val = True if notification_type in request.form else False
    setattr(user, notification_type, val)
    db_session.commit()

    return "success"

@app.route('/update_theme_suggestions',methods=['POST'])
@auth_required()
def update_theme_suggestions():
    user = db_session.query(User).get(request.form['user_id'])
    setattr(user, 'theme_suggestions', request.form['theme_suggestions'])
    db_session.commit()

    return "success"

@app.route('/update_instrument_preferences/<int:instrument_id>',methods=['POST'])
@auth_required()
def update_instrument_preferences(instrument_id):
    instrument = db_session.query(Instrument).get(instrument_id)
    attribute = request.form['attr']
    val = True if attribute in request.form else False
    setattr(instrument, attribute, val)
    db_session.commit()

    # Redirect the user back to the original URL
    original_url = request.headers.get('Referer')
    return redirect(original_url)

@app.route('/index.html')
@app.route('/')
@auth_required()
def index():
    return render_template('index.html')

@app.route("/profile")
@auth_required()
def profile():
    return render_template('profile.html')

@app.route('/upcoming', methods=['GET','POST'])
@auth_required()
def upcoming():
    confirmationForm = ConfirmationForm()
    if confirmationForm.validate_on_submit():
        event_id = confirmationForm.event_id.data
        event = Event.query.filter_by(event_id=event_id).first()
        current_user.events.append(event)
        db_session.commit()

    events = Event.query.all()

    return render_template('upcoming.html',events=events,form = confirmationForm)

def get_user_counts_by_instrument():
    user_counts = defaultdict(int)
    instruments = db_session.query(Instrument).all()

    for instrument in instruments:
        user_counts[instrument.name] += 1

    return dict(user_counts)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({'message': f'{get_user_counts_by_instrument()}'})

@app.route('/unregister/<int:event_id>',methods=['POST'])
@auth_required()
def unregister(event_id):
    event = Event.query.get(event_id)
    current_user.events.remove(event)
    db_session.commit()
    return redirect(url_for('upcoming'))

@app.route('/eventDetails')
@auth_required()
def eventDetails():
    event = Event.query.get(request.args['event_id'])
    print(event.description)
    return render_template('eventDetails.html',event=event)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/update_signup', methods=['POST'])
@auth_required()
def update_signup():
    audition_slot = AuditionSlot.query.get(request.form['audition_id'])
    # If the signup doesn't exist, create a new one
    if audition_slot not in current_user.audition_slots:
        # Check slot is still free
        if audition_slot.user is not None:
            flash('Slot is no longer free!')
            return redirect(url_for('auditions'))
        current_user.audition_slots.append(audition_slot)
        audition_slot.instrument = request.form['instrument']
        audition_slot.level = request.form['level']
    else:
        # TODO: these should probably be separate routes
        #remove the signup
        current_user.audition_slots.remove(audition_slot)
        # TODO: This is clunky and error-prone. Replace with assocation table
        audition_slot.instrument = None
        audition_slot.grade = None
    db_session.commit()

    return redirect(url_for('auditions'))


@app.route('/admin')
@roles_required('admin')
def adminInterface():
    users = User.query.all()
    return render_template('adminInterface.html',users=users)

def generate_instrument_form(subclass):
    attributes = subclass.get_instrument_attributes()

    class InstrumentForm(FlaskForm):
        submit = SubmitField('Add Instrument')

    for attribute in attributes:
        column_type = getattr(subclass, attribute.key).property.columns[0].type
        if isinstance(column_type, Boolean):
            field = BooleanField(attribute.key)
        elif isinstance(column_type, String):
            field = StringField(attribute.key)
        else:
            # Handle other column types as needed
            field = StringField(attribute.key)  # Default to StringField
        setattr(InstrumentForm, attribute.key, field)
    
    return InstrumentForm

@app.template_filter()
def create_instrument_form(subclass):
    Form = generate_instrument_form(subclass)
    return Form()

@app.route('/update_user/<int:user_id>')
@roles_required('admin')
def update_user(user_id):
    user = User.query.get(user_id)
    instruments = [instrument for instrument in  Instrument.__subclasses__()]
    return render_template('updateUser.html',user=user, instruments = instruments)
        
@app.route('/delete_user/<int:user_id>',methods=['POST'])
@roles_required('admin')
def delete_user(user_id):
    user = User.query.get(user_id)
    try:
        db_session.delete(user)
        db_session.commit()
    except IntegrityError as e:
        db_session.rollback()
        print("Integrity error",e)
    return redirect(url_for('adminInterface'))

def instantiate_instrument_form(form_class, request_data):
    return form_class(request_data)

@app.route('/add_instrument/<int:user_id>', methods=['POST'])
@roles_required('admin')
def add_instrument(user_id):
    user = db_session.query(User).get(user_id)
    instrument_type = request.form['instrument_type']
    old_instrument = Instrument.query.filter_by(user_id=user_id,name=instrument_type.lower()).first()
    instruments = [instrument for instrument in  Instrument.__subclasses__()]
    user_instruments = [instrument.name for instrument in  user.instruments]

    instrument_subclass = globals()[instrument_type]  # Get the subclass by name
    if instrument_subclass.__tablename__ in user_instruments:
        print("instrument_already_defined, are you sure you want to override")
    InstrumentForm = generate_instrument_form(instrument_subclass)

    form = InstrumentForm(request.form)
    if form.validate():
        instrument = instrument_subclass()
        for attribute in instrument_subclass.get_instrument_attributes():
            setattr(instrument, attribute.key, getattr(form, attribute.key).data)
        if old_instrument:
            user.instruments.remove(old_instrument)
        user.instruments.append(instrument)
        db_session.commit()

    return redirect(url_for('update_user',user_id=user_id))

@app.route('/delete_instrument/<int:user_id>',methods=['POST'])
@roles_required('admin')
def delete_instrument(user_id):
    user = db_session.query(User).get(user_id)
    instrument_type = request.form['instrument_type']
    old_instrument = Instrument.query.filter_by(user_id=user_id,name=instrument_type.lower()).first()
    user.instruments.remove(old_instrument)
    db_session.commit()
    return redirect(url_for('update_user',user_id=user_id))
