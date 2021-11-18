from zombie.app import app
from flask import jsonify
from marshmallow import ValidationError
from zombie.extensions import db
from sqlalchemy_utils import database_exists, create_database


db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
if not database_exists(db_uri):
    create_database(db_uri)

@app.before_first_request
def create_tables():
    db.create_all()

# setting app level error handlers
@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):  # except ValidationError as err
    return jsonify(err.messages), 400

