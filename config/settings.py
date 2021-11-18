import os
import binascii
from uuid import uuid4

BASEDIR = os.getcwd()
WORKDIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
LOG_LEVEL = "DEBUG"  # CRITICAL / ERROR / WARNING / INFO / DEBUG

SERVER_HOST=os.environ.get("SERVER_HOST")
SERVER_NAME = f'{SERVER_HOST}:{os.environ.get("SERVER_PORT")}'
SECRET_KEY = binascii.b2a_hex(uuid4().bytes).decode("utf-8")


# Flask-Mail.
MAIL_DEFAULT_SENDER = "error-no-reply@@status.com"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


DEBUG_TB_PROFILER_ENABLED=True


db_path = 'sqlite:///' + os.path.join(BASEDIR, 'zombie.db')
db_uri = os.environ.get("DATABASE_URL", db_path)
SQLALCHEMY_DATABASE_URI = db_uri

PROPAGATE_EXCEPTIONS = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True


BEARER = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs' \
        '%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'

