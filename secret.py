import secrets
import os

def generate_secret_key_and_salt():
    """ Set the secret key and salt as environment variables. """

    SECRET_KEY = secrets.token_hex(32)
    SECRET_SALT = secrets.token_hex(16)
    os.environ['SECRET_KEY'] = SECRET_KEY
    os.environ['SECURITY_PASSWORD_SALT'] = SECRET_SALT