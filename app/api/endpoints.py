"""This Module contains endpoints for Api."""

from flask.json import jsonify
from flask_jwt_extended import get_jwt_claims, jwt_required
from flask_restful import Resource

from app.base import api_app as app
from app.models import profile, user

from . import endpoint_blueprint

app.init_app(endpoint_blueprint)
app = app.namespace(
    "Bucketlist",
    description='Operations related to Bucketlist',
    path='/api/v1.0/bucketlist')


class BaseResource(Resource):

    @jwt_required
    def __init__(self, req):
        self.username = get_jwt_claims()['user_credential']
        self.user = user.User.get_user(name=self.username)
        if not self.user:
            self.user = user.User.get_user(email=self.username)
        self.profile = self.user.profile


@app.route('/', endpoint='bucketlist')
class BucketList(BaseResource):

    def get(self):
        """List all the created bucket lists."""
        return jsonify({
            "message": "Not Implemented",
            "user": self.username,
            "buckets": []
        })

    def post(self):
        """Create a new bucket list."""
        return {"message": "Not Implemented"}


@app.route('/<int:bucket_id>', endpoint='bucketlistoperations')
class BucketListOperations(BaseResource):

    def get(self):
        """Get single bucket list."""
        return jsonify({"message": "Not Implemented"})

    def put(self):
        """Update this bucket list."""
        return {"message": "Not Implemented"}

    def delete(self):
        """Delete this single bucket list."""
        return {"message": "Not Implemented"}


@app.route('/<int:bucket_id>/items', endpoint='item')
class Item(BaseResource):

    def post(self):
        """Create a new item in bucket list."""
        return {"message": "Not Implemented"}


@app.route('/<int:bucket_id>/items/<int:item_id>', endpoint='itemoperations')
class ItemOperations(BaseResource):

    def put(self):
        """Update a bucket list item."""
        return {"message": "Not Implemented"}

    def delete(self):
        """Delete an item in a bucket list."""
        return {"message": "Not Implemented"}
