from flask import Blueprint
from flask.json import jsonify
from werkzeug.exceptions import BadRequest, InternalServerError

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def not_found(e):
    return generic_errors("Not found", code=404)


@errors.app_errorhandler(500)
def server_error(e):
    return generic_errors("server error", code=500)


@errors.app_errorhandler(405)
def method_error(e):
    return generic_errors("method not allowed", code=405)


@errors.app_errorhandler(ValueError)
def handle_invalid_arguments(e):
    errors = e.message
    return generic_errors(errors, code=400)


def generic_errors(error, code, errors={}):
    errors["error"] = error
    response = jsonify(errors)
    response.status_code = code
    return response
