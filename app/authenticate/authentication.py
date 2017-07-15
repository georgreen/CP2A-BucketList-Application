"""This module contain registration and login feature."""
import re

import webargs
from flask import jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended.exceptions import (InvalidHeaderError,
                                           NoAuthorizationError)
from flask_restplus import Namespace, Resource, fields
from jwt.exceptions import DecodeError, ExpiredSignatureError
from webargs.flaskparser import parser
from werkzeug.exceptions import InternalServerError

from app.base import autheticate_manager
from app.models import profile, user

app = Namespace(
    "Auth", description='Operations related to Authentication', path='/v1.0')


@parser.error_handler
def handle_error(error):
    """Error handler for malformed register and login requests."""
    errors = {key: "".join(error.messages[key]) for key in error.messages}
    e = ValueError(errors)
    e.message = errors
    raise e


@app.errorhandler(ValueError)
def handle_invalid_arguments(e):
    """Handle malformed request data errors."""
    errors = e.message
    return jsonify(errors)


@app.errorhandler(NoAuthorizationError)
def handle_noauthorization(e):
    """Handle missing authorization in header."""
    return jsonify(e)


@app.errorhandler(InvalidHeaderError)
def handle_invalidheader(e):
    """Handle invalid authorization in header."""
    return jsonify(e)


@app.errorhandler(ExpiredSignatureError)
def handle_expiredtoken(e):
    """Handle expired authorization in header."""
    return jsonify(e)


@app.errorhandler(DecodeError)
def handle_decoderror(e):
    """Handle bad authorization in header."""
    return jsonify(e)


@app.errorhandler(Exception)
def handle_unexpected(e):
    """Handle unexpected errors in this namespace."""

    error = {"message": "Server error something went worng :-("}
    return jsonify(error)


@app.route("/register", endpoint='register')
class Register(Resource):
    """Resource for registration."""

    registration_args = {
        'email': webargs.fields.Str(required=True),
        'password': webargs.fields.Str(required=True),
        'username': webargs.fields.Str(required=True)
    }

    # swagger documentation
    register_args_model = app.model(
        'registration_args', {
            'email': fields.String(required=True),
            'password': fields.String(required=True),
            'username': fields.String(required=True),
        })
    register_response_model = app.model('Register_response', {
        'message': fields.String,
        'status': fields.String,
    })

    @app.doc(body=register_args_model, responses={400: "Bad data"})
    @app.response(401, "Registration Failed", register_response_model)
    @app.marshal_with(register_response_model, code=201)
    def post(self):
        """Register a user."""
        self.args = parser.parse(Register.registration_args, request)
        errors = user.UserSchema().validate(self.args)

        if errors:
            errors = {key: "".join(errors[key]) for key in errors}
            data = {"message": errors, "status": "Registration Failed"}
            return data, 401

        password = self.args['password']
        email = self.args['email']
        username = self.args['username']
        verified_email = Login.verify_credentials(email, password)
        verified_username = Login.verify_credentials(username, password)

        if verified_email is not None:
            msg = "Email exists sign in  or Use another email to sign up"
            data = {"message": msg, "status": "Registration Failed"}
            return data, 400
        if verified_username is not None:
            msg = "Username exists, sign in or Use another username to sign up"
            data = {"message": msg, "status": "Registration Failed"}
            return data, 400
        else:
            new_user, errors = user.UserSchema().load(self.args)
            new_profile = profile.Profile("@" + username, new_user)

            if not errors and new_user.save() and new_profile.save():
                msg = "You registerded succesfully."
                data = {"message": msg, "status": "Registered"}
                return data, 201
            else:
                raise InternalServerError


@app.route("/login", endpoint='login')
class Login(Resource):
    """Resource for Login/Authentication."""

    login_args = {
        'email': webargs.fields.Str(required=True),
        'password': webargs.fields.Str(required=True)
    }

    # swagger documentation
    login_args_model = app.model(
        'login_args', {
            'email': fields.String(required=True),
            'password': fields.String(required=True),
        })
    login_response_model = app.model(
        'Login_repsonse', {
            'message': fields.String,
            'status': fields.String,
            'token': fields.String(default="Denied"),
        })

    @app.response(401, "Login Failed", login_response_model)
    @app.doc(body=login_args_model, responses={400: "Bad data"})
    @app.marshal_with(login_response_model, code=200)
    def post(self):
        """Log a user in."""
        self.args = parser.parse(Login.login_args, request)
        self.args['user_login_credential'] = self.args['email']
        if re.match("^[A-Za-z0-9]+\s?[A-Za-z0-9]+$", self.args['email']):
            self.args["username"] = self.args['email']
            self.args.pop('email')
        errors = user.UserSchema().validate(self.args, partial=True)

        if errors:
            errors = {key: "".join(errors[key]) for key in errors}
            data = {"message": errors, "status": "Login Failed"}
            return data, 400

        password = self.args['password']
        user_login_credential = self.args['user_login_credential']
        verified = Login.verify_credentials(user_login_credential, password)

        if verified:
            msg = "You have been logged in succesfully."
            token = create_access_token(user_login_credential)
            data = {"message": msg, "status": "authunticated", "token": token}
            return data, 200
        elif verified is False:
            msg = "Invalid credentials, wrong password."
            data = {"message": msg, "status": "Login Failed"}
            return data, 401
        else:
            msg = "Please sign up or Use a valid username/email."
            data = {"message": msg, "status": "Login Failed"}
            return data, 401

    @staticmethod
    @autheticate_manager.user_claims_loader
    def add_claims_to_access_token(user):
        """Utility method, allow user information to be Embeded in token."""
        return {'user_credential': user}

    @staticmethod
    def verify_credentials(user_credential="", password=""):
        """Utility method, autheticate user information."""
        email = None
        username = None
        if re.match("^[A-Za-z0-9]+\s?[A-Za-z0-9]+$", user_credential):
            email = False
            username = True
        else:
            email = True
            username = False

        query = None
        if email:
            query = user.User.get_user(email=user_credential)
        elif username:
            query = user.User.get_user(name=user_credential)

        if query:
            return query.authenticate_password(password)
        return query
