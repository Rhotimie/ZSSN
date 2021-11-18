from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_marshmallow import Marshmallow


"""
This is useful when porting from one database to the other as their naming conventions are different
so sqlalchemy sticks to this convention irrespective of the database type(MYSQL/POSTGRESQL/MS SQL)
ix --> index
uq --> unique constraint
ck --> check constraint
fk --> foreign key constraint
pk --> primary key constraint
"""
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

debug_toolbar = DebugToolbarExtension()
mail = Mail()
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

"""
ma is a Marshmallow object that can talk to our flask app
"""
ma = Marshmallow()

