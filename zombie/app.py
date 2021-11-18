import os
import logging
from logging.handlers import SMTPHandler
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, render_template, Blueprint
from flask_migrate import Migrate
from flask_cors import CORS
from zombie.blueprints.api import api_bp

from zombie.extensions import debug_toolbar, mail, db, ma


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.settings")
    app.config.from_pyfile("settings.py", silent=True)

    app.url_map.strict_slashes = False


    if settings_override:
        app.config.update(settings_override)

    CORS(app, supports_credentials=True)

    global jwt
    migrate = Migrate(app, db)

    middleware(app)
    error_templates(app)
    exception_handler(app)

    app.register_blueprint(api_bp, url_prefix="/api")
    template_processors(app)
    extensions(app)

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    ma.init_app(app)
    debug_toolbar.init_app(app)
    mail.init_app(app)
    db.init_app(app)

    return None

def template_processors(app):
    """
    Register 0 or more custom template processors (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    # python utilities
    app.jinja_env.globals.update(str=str)
    app.jinja_env.globals.update(enumerate=enumerate)
    app.jinja_env.globals.update(int=int)
    app.jinja_env.globals.update(len=len)
    app.jinja_env.globals.update(list=list)
    app.jinja_env.globals.update(range=range)
    app.jinja_env.globals.update(os=os)
    app.jinja_env.globals.update(getattr=getattr)


    return app.jinja_env


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
        Render a custom template for a specific status.
        Source: http://stackoverflow.com/a/30108946

        :param status: Status as a written name
        :type status: str
        :return: None
        """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, "code", 500)
        return render_template("errors/{0}.html".format(code)), code

    for error in [404, 429, 500]:
        app.errorhandler(error)(render_status)

    return None


def exception_handler(app):
    """
    Register 0 or more exception handlers (mutates the app passed in).

    SET Debug=False, inside config.settings for this to work

    :param app: Flask application instance
    :return: None
    """
    mail_handler = SMTPHandler(
        (app.config.get("MAIL_SERVER"), app.config.get("MAIL_PORT")),
        app.config.get("MAIL_USERNAME"),
        [app.config.get("MAIL_USERNAME")],
        "[Exception handler] A 5xx was thrown",
        (app.config.get("MAIL_USERNAME"), app.config.get("MAIL_PASSWORD")),
        secure=(),
    )

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(
        logging.Formatter(
            """
    Time:               %(asctime)s
    Message type:       %(levelname)s


    Message:

    %(message)s
    """
        )
    )
    app.logger.addHandler(mail_handler)

    return None

app = create_app()


from zombie.app_settings.app_config import *

