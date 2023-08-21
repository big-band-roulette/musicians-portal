from flask import Flask, url_for, redirect,render_template, request
from flask_security import Security, roles_required,current_user, auth_required, \
     SQLAlchemySessionUserDatastore
from database import db_session
from models import User, Role, Audition, AuditionUserLink, Event
from config import Config
from flask_mailman import Mail
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField
from flask_wtf.csrf import CSRFProtect
# Load environment variables from .env file
load_dotenv()

# Create app
app = Flask(__name__)
app.config.from_object(Config)
crsf = CSRFProtect(app)
# class R(Request):
#     # Whitelist SRCF and/or custom domains to access the site via proxy.
#     trusted_hosts = {"bbr.soc.srcf.net","dev.bigbandroulette.com"}
# app.request_class = R

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
app.security = Security(app, user_datastore)

# mail setup
mail = Mail(app)

# confirmation form for the register interest
class ConfirmationForm(FlaskForm):
    event_id = StringField('Event ID')
    submit = SubmitField('Submit')

# Views

@app.route("/auditions")
@auth_required()
def auditions():
    user_id = current_user.id
    auditions = Audition.query.all()
    signups = AuditionUserLink.query.filter_by(user_id=user_id).all()
    signed_up_ids = [signup.audition_id for signup in signups]

    labelled_auditions = [
        {'name': audition.name, 'id': audition.id, 'signed_up': audition.id in signed_up_ids} 
        for audition in auditions
        ]

    return render_template('auditions.html',
                           auditions=labelled_auditions)

@app.route('/index.html')
@app.route('/')
def index():
    return redirect('/login')

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
    return render_template('eventDetails.html',event=event)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/update_signup', methods=['POST'])
@auth_required()
def update_signup():
    signup_update = request.form
    audition_id = list(signup_update.keys())[0]
    # Assuming you have a way to identify the current user, retrieve their signups
    user_id = current_user.id

    # Retrieve the Signup object for the current user and audition
    signup = AuditionUserLink.query.filter_by(user_id=user_id, audition_id=audition_id).first()

    # If the signup doesn't exist, create a new one
    if not signup:
        signup = AuditionUserLink(user_id=user_id, audition_id=audition_id)
        db_session.add(signup)
        db_session.commit()
    else:
        #remove the signup
        db_session.delete(signup)
        db_session.commit()

    return redirect(url_for('auditions'))


@app.route('/admin')
@roles_required('admin')
def adminInterface():
    return render_template('adminInterface.html')
