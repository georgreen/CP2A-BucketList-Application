"""This Module initilizes application with specified configurations.

It contains new_app which is a app factory method, it initializes application

The base Model class(BaseModel)is defined in this module, it defines common
properties for models used in application.
"""

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy

from config import config

# database instance of sqlachemy provides all database operations.
database = SQLAlchemy()

# json_schema provide utilities to model classes as dictionary objects.
json_schema = Marshmallow()

# api_app instance of Api class from flask_restplus, provide utilities for
# defining api's endpoints and Resources
api_app = Api(
    title='BucketList Api',
    version='1.0',
    description=""" The Brighter side of BucketList: Imagine,
    dream then accoplish.""",
    contact="georgreen.ngunga@andela.com")

# authentication manager
autheticate_manager = JWTManager()


def new_app(enviroment="default"):
    """Factory Method that creates an instance of the app with the given config.

    Args:
        enviroment (str): Specify the configuration to initilize app with.

    Returns:
        app (Flask): it returns an instance of Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config[enviroment])
    database.init_app(app)
    json_schema.init_app(app)
    autheticate_manager.init_app(app)

    # register blue prints here
    from app import api
    app.register_blueprint(api.endpoint_blueprint)

    from app import errors
    app.register_blueprint(errors.errors)

    from app import authenticate
    app.register_blueprint(authenticate.authenticate_blueprint)

    return app


class BaseModel(object):
    """Models, the base model which all other models created inherit from.

    It provide utility methods enabling object to be saved and deleted.
    """

    def save(self):
        """Save an instance of a model to the respective table.

        Args:
            self: specify the object to be saved to the table

        Returns:
            True if saving operation was succefull else, False
        """
        saved = None
        try:
            database.session.add(self)
            database.session.commit()
            saved = True
        except Exception as e:
            saved = False
            print(e)
            database.session.rollback()
        return saved

    def delete(self):
        """Delete an instance of a model to the respective table.

        Args:
            self: specify the object to be saved to the table

        Returns:
            True if delete operation was succefull else. False
        """
        deleted = None
        try:
            database.session.delete(self)
            database.session.commit()
            deleted = True
        except Exception:
            deleted = False
            database.session.rollback()
        return deleted
