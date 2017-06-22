from flask import Blueprint

api = Blueprint('api', __name__)


def import_local_modules():
    from . import endpoints
    return endpoints


endpoint = import_local_modules()
