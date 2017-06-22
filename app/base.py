"""This Module initilizes application with specified configurations."""

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy

from config import config

"""database instance of sqlachemy provides all database operations."""
database = SQLAlchemy()
"""json_schema provide utilities to model classes as dictionary objects"""
json_schema = Marshmallow()
"""api provide utilies to implement the Api's resources"""
api_utilies = Api()


def new_app(enviroment="default"):
    """Factory Method that creates an instance of the app with the given config.

    Args:
        enviroment (str): Specify the configuration to initilize app with.

    Returns:
        app (Flask): The returns an instance of Flask.
    """
    app = Flask(__name__)
    api_utilies.init_app(app)
    app.config.from_object(config[enviroment])
    database.init_app(app)
    json_schema.init_app(app)

    # register blue prints here
    from app import api
    app.register_blueprint(api.api)

    from app import errors
    app.register_blueprint(errors.errors)

    from app import authenticate
    app.register_blueprint(authenticate.authenticate)

    return app


class BaseModel(object):
    """Models the base model, which all other models created inherit from.

    It provide utility methods enabling object to be saved and deleted.
    """

    def save(self):
        """Save an instance of a model to the respective table.

        Args:
            self: specify the object to be saved to the table
        """
        saved = None
        try:
            database.session.add(self)
            database.session.commit()
            saved = True
        except Exception:
            saved = False
        return saved

    def delete(self):
        """Delete an instance of a model to the respective table.

        Args:
            self: specify the object to be saved to the table
        """
        deleted = None
        try:
            database.session.delete(self)
            database.session.commit()
            deleted = True
        except Exception:
            deleted = False
        return deleted
