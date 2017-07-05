from flask import Blueprint

endpoint_blueprint = Blueprint('api_blueprint', __name__)


def import_local_modules():
    from . import endpoints
    return endpoints


endpoint = import_local_modules()
