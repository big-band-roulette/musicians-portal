import os 
import secrets
from passlib import totp

class Config:
  # Generate a nice key using secrets.token_urlsafe()
  SECRET_KEY = os.environ.get("SECRET_KEY")# or secrets.token_urlsafe(32)
  # Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
  # Generate a good salt using: secrets.SystemRandom().getrandbits(128)
  SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")# or secrets.token_urlsafe(16)
  # Don't worry if email has findable domain
  SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}

  #allow user registration
  SECURITY_REGISTERABLE = True 
  SECURITY_PASSWORD_CHECK_BREACHED = 'strict'
  SECURITY_PASSWORD_COMPLEXITY_CHECKER = 'zxcvbn'
  SECURITY_ZXCBN_MINIMUM = 3

  #force email confirmation on login
  SECURITY_CONFIRMABLE = False

  #force register email
  SECURITY_SEND_REGISTER_EMAIL = False

  # Adding two factor authentication
  SECURITY_TWO_FACTOR = True
  SECURITY_TWO_FACTOR_REQUIRED = False
  SECURITY_TOTP_SECRETS = {1: totp.generate_secret()}
  SECURITY_TOTP_ISSUER = "Big Band Roulette"

  # change the post login page to auditions
  SECURITY_POST_LOGIN_VIEW = '/auditions'

  # Tracking login statistics 
  SECURITY_TRACKABLE = True

  # Recovering Passwords
  SECURITY_CHANGEABLE = True
  SECURITY_RECOVERABLE = True # TODO This should be changed to true, when we have an email extension configured
  SECURITY_EMAIL_SENDER = "no-reply@bigbandroulette.com" # TODO this might not be the right setting...


  # mail setup

  # Select the appropriate configuration based on environment
  MAIL_SERVER = os.environ.get('MAIL_SERVER')  # Use a test SMTP server for local testing
  MAIL_PORT = os.environ.get('MAIL_PORT')
  MAIL_USE_TLS = True if os.environ.get('MAIL_USE_TLS') == 'True' else False
  MAIL_USE_SSL = True if os.environ.get('MAIL_USE_SSL') == 'True' else False
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')