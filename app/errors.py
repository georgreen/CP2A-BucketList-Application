from flask import Blueprint
from flask.json import jsonify

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def not_found(e):
    return jsonify({'error': 'not found'}), 404
