import os

DEBUG = False


MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


DEBUG_TB_INTERCEPT_REDIRECTS=False
DEBUG_TB_PROFILER_ENABLED=False

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False

