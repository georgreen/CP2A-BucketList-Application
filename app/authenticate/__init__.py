from flask import Blueprint

authenticate = Blueprint('authenticate', __name__)


def import_local_modules():
    from . import authentication
    return authentication


auth = import_local_modules()
