"""This Module initilizes application with specified configurations.

It contains new_app which is a app factory method, it initializes application

The base Model class(BaseModel)is defined in this module, it defines common
properties for models used in application.
"""

from flask import Blueprint, Flask, abort, json, request
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy

from app import errors
from config import config

# database instance of sqlachemy provides all database operations.
database = SQLAlchemy()

# json_schema provide utilities to model classes as dictionary objects.
json_schema = Marshmallow()

# api nstance of Api class from flask_restplus, provide utilities for
# defining api's endpoints and Resources

api_blueprint = Blueprint('api', __name__, url_prefix="/api")

api = Api(
    app=api_blueprint,
    title='BucketList Api',
    version='1.0',
    description=""" The Brighter side of BucketList: Imagine,
    dream then accomplish.""",
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
    flask = Flask(__name__)
    flask.config.from_object(config[enviroment])
    database.init_app(flask)
    json_schema.init_app(flask)
    autheticate_manager.init_app(flask)

    flask.register_blueprint(errors.errors)
    flask.register_blueprint(api_blueprint)

    # add authentication and endpoints to api
    from app.authenticate import authentication
    api.add_namespace(authentication.app)

    from app.endpoint import endpoints
    api.add_namespace(endpoints.app)

    @flask.after_request
    def check_response(response):
        """Utility to handle response before dispatch."""
        if response.status_code == 301:
            path = request.path
            if path[-1] != '/':
                path = path + '/'
            response.data = json.dumps({
                "message":
                "This URL:" + request.path + " is not correct",
                "Url":
                path
            })
            response.content_type = 'application/json'
            response.status_code = 301
        elif (response.content_type != 'application/json' and
              response.status_code != 200):
            response.data = json.dumps({
                "message":
                "Oops something went wrong :-("
            })
            response.content_type = 'application/json'
            response.status_code = 500
        return response

    return flask


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
