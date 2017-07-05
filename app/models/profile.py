"""This module contains Model a user's Profile."""

from sqlalchemy.orm.collections import attribute_mapped_collection

from app.base import BaseModel, database
from app.models import bucketlist

budy = database.Table('budys',
                      database.Column("user_id", database.Integer,
                                      database.ForeignKey('users.id')),
                      database.Column("profile_id", database.Integer,
                                      database.ForeignKey('profiles.id')))


class Profile(database.Model, BaseModel):
    """Model a User profile in the application."""

    __tablename__ = "profiles"
    id = database.Column(database.Integer, primary_key=True)
    handle = database.Column(database.String(64), nullable=False, unique=True)
    date_created = database.Column(
        database.DateTime, default=database.func.now())
    last_seen = database.Column(
        database.DateTime,
        default=database.func.now(),
        onupdate=database.func.now())
    status = database.Column(database.String(140), default="SELBSTÜBERWINDUNG")

    owner = database.relationship(
        "User", uselist=False, backref='profile', cascade="all, delete-orphan")

    mentors = database.relationship(
        "User",
        secondary=budy,
        collection_class=attribute_mapped_collection('username'),
        backref=database.backref('followers'))

    bucket_lists = database.relationship(
        "Bucket",
        collection_class=attribute_mapped_collection('name'),
        cascade="all, delete-orphan")

    next_bucket_id = database.Column(database.Integer, default=0)
    next_item_id = database.Column(database.Integer, default=0)

    def __init__(self, handle, owner):
        """Initilize the profile with required information."""
        self.handle = handle
        self.owner = owner

    def get_bucket(self, name=None, bucket_id=None, id=None):
        bucket = None
        if name:
            bucket = self.bucket_lists.get(name, None)
        elif bucket_id or bucket_id == 0:
            bucket = bucketlist.Bucket.get_bucket(
                asset_id=bucket_id, profile_id=self.id)
        elif id or id == 0:
            bucket = bucketlist.Bucket.get_bucket(id=id, profile_id=self.id)
        return bucket

    def add_bucket(self, name):
        new_bucket = bucketlist.Bucket(name)
        new_bucket.asset_id = self.next_bucket_id
        self.bucket_lists[new_bucket.name] = new_bucket

        if new_bucket.save() and self.save():
            self.next_bucket_id += 1
            return self.save()
        else:
            return False
        return None

    def get_item(self, item_id=None, name=None, id=None):
        item = None
        if item_id or item_id == 0:
            item = bucketlist.Item.get_item(
                asset_id=item_id, profile_id=self.id)
        elif name:
            item = bucketlist.Item.get_item(name=name, profile_id=self.id)
        elif id or id == 0:
            item = bucketlist.Item.get_item(id=id, profile_id=self.id)
        return item

    def add_item(self, name, description="TO DO", buc_id=None, buc_name=None):
        bucket = None
        if buc_name:
            bucket = self.get_bucket(name=buc_name)
        elif buc_id or buc_id == 0:
            bucket = self.get_bucket(asset_id=buc_id)

        if bucket:
            new_item = bucketlist.Item(name, description)
            new_item.asset_id = self.next_item_id
            bucket.items[new_item.name] = new_item
            if bucket.save() and new_item.save() and self.save():
                self.next_item_id += 1
                return self.save()
            else:
                return False
        return None

    def edit_asset(self, asset_id=None, name=None, description=None,
                   item=None):

        if item:
            edit_item = self.get_item(item_id=asset_id)
            bucket = self.get_bucket(id=edit_item.bucket_id)
            if edit_item and bucket:
                if name:
                    bucket.items[name] = bucket.items.pop(edit_item.name)
                    bucket.items[name].name = name
                if description:
                    bucket.items[name].description = description

                return edit_item.save() and self.save() and bucket.save()

        if not item:
            edit_bucket = self.get_bucket(bucket_id=asset_id)
            if name and edit_bucket:
                self.bucket_lists[name] = self.bucket_lists.pop(
                    edit_bucket.name)
                edit_bucket.name = name
                return edit_bucket.save() and self.save()

        return None

    def delete_asset(self, asset_id=None, name=None, item=False):
        assert_to_delete = None
        if item and (asset_id or asset_id == 0):
            assert_to_delete = self.get_item(item_id=asset_id)
        elif item and name:
            assert_to_delete = self.get_item(name=name)
        elif asset_id or asset_id == 0:
            assert_to_delete = self.get_bucket(bucket_id=asset_id)
        elif name:
            assert_to_delete = self.get_bucket(name=name)

        if assert_to_delete:
            return assert_to_delete.delete()
        return assert_to_delete

    @classmethod
    def get_profile(cls, handle=None):
        """Get a Profile from the table profiles.

        Args:
            cls (Profile): Model to be queried
            handle (str): Specify handle for user

        Returns:
            instance of Profile if succesfull, else None
        """
        if handle:
            return cls.query.filter_by(handle=handle).first()

    @classmethod
    def get_profiles(cls):
        """Get a Profile from the table profiles.

        Args:
            cls (Profile): Model to be queried

        Returns:
            list of all profile instances
        """
        return cls.query.all()
