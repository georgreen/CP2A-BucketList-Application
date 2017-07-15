"""This Module contains endpoints for Api."""

import re

import webargs
from flask import request, url_for
from flask.json import jsonify
from flask_jwt_extended import get_jwt_claims, jwt_required
from flask_restplus import Namespace, Resource, fields
from sqlalchemy import or_
from webargs.flaskparser import parser

from app.models import bucketlist, user

app = Namespace(
    "Bucketlist",
    description='Operations related to Bucketlist',
    path='/v1.0/bucketlist')


def make_response(values, code, headers=None):
    """Utility function that assemble's endpoint responses."""
    response = jsonify(values)
    response.status_code = code
    if headers:
        response.headers["Link"] = headers.get('link')
    return response


def validat_str(name):
    """Utility function that validates names for buckets/items."""
    if len(name.strip()) == 0:
        return False
    if re.match("^[A-Za-z0-9_\s]*$", name):
        return True
    return False


# swagger documentation
item_model = app.model('Item', {
    'id': fields.Integer(),
    'name': fields.String(),
    'description': fields.String(),
    'bucket id': fields.String(),
    'date created': fields.String(),
    'date modified': fields.String(),
    'done': fields.Boolean
})

bucket_model = app.model('BucketList', {
    'id': fields.Integer(),
    'name': fields.String(),
    'items': fields.Nested(item_model),
    'created by': fields.String(),
    'date created': fields.String(),
    'date modified': fields.String()
})


class BaseResource(Resource):
    """Base Resource, provide authorization, access to user and profile."""

    api = app

    @jwt_required
    def __init__(self, req):
        """Initialize username, user object and the user profile."""
        self.username = get_jwt_claims()['user_credential']
        self.user = user.User.get_user(name=self.username)
        if not self.user:
            self.user = user.User.get_user(email=self.username)
        self.profile = self.user.profile


@app.header("Authorization", "Access tokken", required=True)
@app.route('/', endpoint='bucketlist')
class BucketList(BaseResource):
    """Resource for BucketList."""

    # swagger documentation
    query_args = {
        "limit": webargs.fields.Int(),
        "page": webargs.fields.Int(),
        "q": webargs.fields.Str()
    }

    @app.doc(params={
        "limit": "limit the results",
        "page": "page required",
        "q": "Search term"
    })
    def get(self):
        """List all the created bucket lists."""
        args = parser.parse(BucketList.query_args, request)
        limit = args.get("limit")
        page = args.get("page")
        query = args.get("q")
        if limit and limit > 100:
            limit = 100
        if not limit or limit < 1:
            limit = 20
        if not page:
            page = 1

        get_bucket = bucketlist.Bucket.query.filter_by(
            profile_id=self.profile.id)
        if query:
            get_bucket = get_bucket.filter(
                or_(
                    bucketlist.Bucket.name.ilike("%" + query + "%"),
                    bucketlist.Bucket.name.contains(query)))
        paginate = get_bucket.paginate(page, limit, True)

        headers = {}
        link = []
        if paginate.has_next:
            url_for_next = url_for(
                'api.bucketlist',
                q=query,
                limit=limit,
                page=paginate.next_num,
                _external=True)
            link.append("<" + url_for_next + ">" + "; rel='next'")

        if paginate.has_prev:
            url_for_prev = url_for(
                'api.bucketlist',
                q=query,
                limit=limit,
                page=paginate.prev_num,
                _external=True)
            link.append("<" + url_for_prev + ">" + "; rel='prev'")
        headers["link"] = link

        data = {bucket.asset_id: bucket.to_dict() for bucket in paginate.items}
        return make_response(
            {
                "message": "User buckets",
                "current page": page,
                "total pages": paginate.pages,
                "user": self.username,
                "buckets": data
            },
            200,
            headers=headers)

    # swagger documentation
    create_bucket_args = {"name": webargs.fields.Str(required=True)}
    create_bucket_args_model = app.model(
        "create_bucket_args", {"name": fields.String(required=True)})

    @app.doc(body=create_bucket_args_model)
    def post(self):
        """Create a new bucket list."""
        args = parser.parse(BucketList.create_bucket_args, request)

        # validate name
        name = args["name"]
        if not validat_str(name):
            return {
                "message":
                "bucket name can only contain letters numbers and space"
            }, 400

        # query if bucket exists
        if self.profile.get_bucket(name):
            return {"message": "Bucket: " + name + " exists"}, 400
        # create bucket
        if not self.profile.add_bucket(name):
            return {"message": "Server was unable to process request"}, 500

        # get bucket
        data = self.profile.get_bucket(name).to_dict()
        return make_response({
            "message": "bucket created succesfully",
            "user": self.username,
            "bucket": data
        }, 201)


@app.header("Authorization", "Access tokken", required=True)
@app.route('/<int:bucket_id>', endpoint='bucketlistoperations')
class BucketListOperations(BaseResource):
    """Resource for Bucketlist Operations."""

    def get(self, bucket_id):
        """Get single bucket list."""
        data = self.profile.bucket_lists.get(bucket_id)
        if data is None:
            return {"message": "Bucket not found"}, 404

        data = data.to_dict()
        return make_response({"message": "bucket found", "bucket": data}, 200)

    # swagger documentation
    update_bucket_args = {"name": webargs.fields.Str(required=True)}
    update_bucket_args_model = app.model(
        "update_bucket_args", {"name": fields.String(required=True)})

    @app.doc(body=update_bucket_args_model)
    def put(self, bucket_id):
        """Update this bucket list."""
        args = parser.parse(BucketListOperations.update_bucket_args, request)
        name = args["name"]

        if not validat_str(name):
            return {
                "message":
                "bucket name can only contain letters numbers and space"
            }, 400

        edit = self.profile.edit_asset(
            item=False, name=name, asset_id=bucket_id)
        if edit is None:
            return {"message": "Bucket not found"}, 404
        if not edit:
            return {"message": "Bucket not edited"}, 422
        else:
            data = self.profile.bucket_lists.get(bucket_id).to_dict()
            return make_response({
                "message": "Updated bucket succesfully",
                "bucket": data
            }, 201)

    def delete(self, bucket_id):
        """Delete this single bucket list."""
        deleted = self.profile.delete_asset(asset_id=bucket_id)
        if deleted is None:
            return {"message": "Bucket not found"}, 404
        elif not deleted:
            return {"message": "Bucket not deleted"}, 422
        else:
            return {"message": "Bucket deleted succesfully"}, 200


@app.header("Authorization", "Access tokken", required=True)
@app.route('/<int:bucket_id>/items', endpoint='item')
class Item(BaseResource):
    """Resource for Item."""

    # swagger documentation
    create_items_args = {
        "name": webargs.fields.Str(required=True),
        "description": webargs.fields.Str()
    }
    create_items_args_model = app.model(
        "create_items_args",
        {"name": fields.String(required=True),
         "description": fields.String()})

    @app.doc(body=create_items_args_model)
    def post(self, bucket_id):
        """Create a new item in bucket list."""
        args = parser.parse(Item.create_items_args, request)
        name = args["name"]
        description = args.get("description", "Let's Do this")

        # validate name
        if not validat_str(name):
            return {
                "message":
                "bucket name can only contain letters numbers and space"
            }, 400

        # get bucket
        bucket = self.profile.bucket_lists.get(bucket_id)
        if bucket is None:
            return {"message": "Bucket not found"}, 404
        # get item
        item = self.profile.get_item(name=name)
        if item:
            return {"message": "Item " + name + " exists"}, 400

        # create item
        if not self.profile.add_item(
                name=name, description=description, buc_id=bucket_id):
            return {"message": "Server error: Creating item failed"}, 500
        # get item
        data = self.profile.get_item(name=name).to_dict()
        return {
            "message": "Item created succesfully",
            "bucket_id": bucket_id,
            "item": data
        }, 201


@app.header("Authorization", "Access tokken", required=True)
@app.route('/<int:bucket_id>/items/<int:item_id>', endpoint='itemoperations')
class ItemOperations(BaseResource):
    """Resource for Item Operations."""

    def get(self, bucket_id, item_id):
        """Get Single Item."""
        bucket = self.profile.bucket_lists.get(bucket_id)
        if not bucket:
            return {"message": "Bucket specified does not exist"}, 404
        item = bucket.items.get(item_id)
        if not item:
            return {
                "mesage": "Item specified does not exist in the bucketlist"
            }, 404
        data = item.to_dict()
        return {
            bucket.asset_id: {
                "bucket name": bucket.name,
                "id": bucket.asset_id,
                "item": data,
                "create by": bucket.created_by
            },
            "message": "Item found in bucket"
        }, 200

    update_items_args = {"done": webargs.fields.Boolean(required=True)}
    update_items_args_model = app.model(
        "update_items_args", {"done": fields.Boolean(required=True)})

    @app.doc(body=update_items_args_model)
    def patch(self, bucket_id, item_id):
        """Patch a bucket list item."""
        args = parser.parse(ItemOperations.update_items_args, request)
        done = args.get("done")

        # get item
        item = self.profile.get_item(item_id=item_id, buc_id=bucket_id)
        bucket = self.profile.get_bucket(bucket_id=bucket_id)
        if not item or not bucket and item.bucket_id != bucket.id:
            return {"message": "Item not found in bucket"}, 404

        # editted
        edit = self.profile.edit_asset(
            item=True, done=done, asset_id=item_id, buc_id=bucket_id)

        if not edit:
            return {"message": "Unable to edit item"}, 422

        # get item
        return {
            "message": "Patched Item succesfully",
            "item": item.to_dict()
        }, 200

    # swagger documrntation
    edit_items_args = {
        "name": webargs.fields.Str(),
        "description": webargs.fields.Str()
    }
    edit_items_args_model = app.model("edit_items_args", {
        "name": fields.String,
        "description": fields.String
    })

    @app.doc(body=edit_items_args_model)
    def put(self, bucket_id, item_id):
        """Update a bucket list item."""
        args = parser.parse(ItemOperations.edit_items_args, request)
        name = args.get("name", False)
        description = args.get("description", False)

        if not (name or description):
            return {
                "message":
                "Please enter field to be editted name or description"
            }, 400

        # validate name
        if name and (not validat_str(name)):
            return {
                "message":
                "Item name can only contain letters numbers and space"
            }, 400

        # get item

        item = self.profile.get_item(item_id=item_id, buc_id=bucket_id)
        bucket = self.profile.get_bucket(bucket_id=bucket_id)
        if not item or not bucket:
            return {"message": "Unable to find bucket/item"}, 404

        if item.bucket_id != bucket.id:
            return {"message": "Item not found in bucket"}, 404

        # editted
        edit = self.profile.edit_asset(
            item=True,
            name=name,
            description=description,
            asset_id=item_id,
            buc_id=bucket_id)
        if not edit:
            return {"message": "Unable to edit item"}, 422

        return {
            "message": "Updated Item succesfully",
            "item": item.to_dict()
        }, 201

    def delete(self, bucket_id, item_id):
        """Delete an item in a bucket list."""
        bucket = self.profile.get_bucket(bucket_id=bucket_id)
        item = self.profile.get_item(item_id=item_id, buc_id=bucket_id)
        if bucket is None or item is None:
            return {"message": "Bucket/item specified does not exist"}, 404
        elif bucket.id != item.bucket_id:
            return {
                "message": "Item not found in bucketlist:" + bucket.name
            }, 404
        deleted_item = self.profile.delete_asset(
            item=True, asset_id=item_id, buc_id=bucket_id)
        if not deleted_item:
            return {"message": "Item was not delted"}, 422

        return {"message": "Item deleted succesfully"}, 200
