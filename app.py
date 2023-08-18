import os
from passlib import totp
from flask import Flask, flash, url_for, redirect,render_template, Request, request
from flask_security import Security, roles_required,current_user, auth_required, \
     SQLAlchemySessionUserDatastore
from database import db_session, init_db
from models import User, Role, Audition, AuditionUserLink, Event
from dataSimulator import add_simulated_data
from secret import generate_secret_key_and_salt

generate_secret_key_and_salt()

# Create app
app = Flask(__name__)

class R(Request):
    # Whitelist SRCF and/or custom domains to access the site via proxy.
    trusted_hosts = {"bbr.soc.srcf.net"}
app.request_class = R

# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT")
# Don't worry if email has findable domain
app.config["SECURITY_EMAIL_VALIDATOR_ARGS"] = {"check_deliverability": False}

#allow user registration
app.config['SECURITY_REGISTERABLE'] = True 
app.config['SECURITY_PASSWORD_CHECK_BREACHED'] = 'strict'
app.config['SECURITY_PASSWORD_COMPLEXITY_CHECKER'] = 'zxcvbn'
app.config['SECURITY_ZXCBN_MINIMUM'] = 3

#force email confirmation on login
app.config["SECURITY_CONFIRMABLE"] = False

#force register email
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False

# Adding two factor authentication
app.config["SECURITY_TWO_FACTOR"] = True
app.config['SECURITY_TWO_FACTOR_REQUIRED'] = False
app.config["SECURITY_TOTP_SECRETS"] = {1: totp.generate_secret()}
app.config["SECURITY_TOTP_ISSUER"] = "Big Band Roulette"

# change the post login page to auditions
app.config['SECURITY_POST_LOGIN_VIEW'] = '/auditions'

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
app.security = Security(app, user_datastore)

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

@app.route('/')
def index():
    return redirect('/login')

@app.route("/profile")
@auth_required()
def profile():
    return render_template('profile.html')

@app.route('/upcoming')
@roles_required('auditioned')
def upcoming():
    gigs = Event.query.all()
    return render_template('upcoming.html',gigs=gigs)


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
    else:
        #remove the signup
        db_session.delete(signup)

    db_session.commit()
    flash('Signup status updated successfully')
    return redirect(url_for('auditions'))


@app.route('/admin')
@roles_required('admin')
def adminInterface():
    return render_template('adminInterface.html')


# one time setup
with app.app_context():
    init_db()
    #add_simulated_data(app,db_session)

if __name__ == '__main__':
    # run application (can also use flask run)
    # Toggle for debug config
    #app.config['DEBUG'] = True
    app.run(port=5001)