"""This module contains Model a user's Profile."""

from app.base import BaseModel, database
from app.models import bucketlist
from sqlalchemy.orm.collections import attribute_mapped_collection

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
    status = database.Column(database.String(140), default="SELBSTUBERWINDUNG")

    owner = database.relationship(
        "User", uselist=False, backref='profile', cascade="all, delete-orphan")

    mentors = database.relationship(
        "User",
        secondary=budy,
        collection_class=attribute_mapped_collection('username'),
        backref=database.backref('followers'))

    bucket_lists = database.relationship(
        "Bucket",
        collection_class=attribute_mapped_collection('asset_id'),
        cascade="all, delete-orphan")

    next_bucket_id = database.Column(database.Integer, default=0)
    next_item_id = database.Column(database.Integer, default=0)

    def __init__(self, handle, owner):
        """Initilize the profile with required information."""
        self.handle = handle
        self.owner = owner

    def get_bucket(self, name=None, bucket_id=None, id=None):
        """Get a bucket from the table buckets.

        Args:
            name(str): Name of bucket
            bucket_id(int): Specify's asset_id for a bucket_id
            id(int): Specify bucket's id in the whole system

        Returns:
            instance of a bucket if succesfull, else None
        """
        bucket = None
        if name:
            bucket = bucketlist.Bucket.get_bucket(
                name=name, profile_id=self.id)
        elif bucket_id or bucket_id == 0:
            # bucket = bucketlist.Bucket.get_bucket(
            #     asset_id=bucket_id, profile_id=self.id)
            bucket = self.bucket_lists.get(bucket_id)
        elif id or id == 0:
            bucket = bucketlist.Bucket.get_bucket(id=id, profile_id=self.id)
        return bucket

    def add_bucket(self, name):
        """Create a bucket.

        Args:
            name(str): Name of the bucket

        Returns:
            True if succesfull, False if bucket was not saved and None if error
            occured.
        """
        new_bucket = bucketlist.Bucket(name)
        new_bucket.created_by = self.owner.username
        new_bucket.profile_id = self.id
        new_bucket.asset_id = self.next_bucket_id

        if new_bucket.save() and self.save():
            self.bucket_lists[new_bucket.asset_id] = new_bucket
            self.next_bucket_id += 1
            return self.save()
        else:
            return None

    def get_item(self, item_id=None, name=None, id=None, buc_id=None):
        """Get an item from the table items.

        Args:
            name(str): Name of item
            item_id(int): Specify's asset_id for an item
            id(int): Specify item's id in the whole system

        Returns:
            instance of a item if succesfull, else None
        """
        item = None
        if (item_id or item_id == 0) and (buc_id or buc_id == 0):
            # item = bucketlist.Item.get_item(
            #     asset_id=item_id, profile_id=self.id)
            if self.bucket_lists.get(buc_id):
                item = self.bucket_lists.get(buc_id).items.get(item_id)
        elif name:
            item = bucketlist.Item.get_item(name=name, profile_id=self.id)
        elif id or id == 0:
            item = bucketlist.Item.get_item(id=id, profile_id=self.id)
        return item

    def add_item(self, name, description="TO DO", buc_id=None, buc_name=None):
        """Create an item.

        Args:
            name(str): Name of the item
            description(str): Give description of item, saved along the item
            buc_name(str):Name for the bucket item will be added to this bucket
            buc_id(int): asset_id for bucket item will be added here

        Returns:
            True if succesfull, False if item was not saved and None if the
            bucket does not exist.
        """
        bucket = None
        if buc_name:
            bucket = self.get_bucket(name=buc_name)
        elif buc_id or buc_id == 0:
            bucket = self.get_bucket(bucket_id=buc_id)

        if bucket:
            new_item = bucketlist.Item(name, description)
            new_item.profile_id = self.id
            new_item.asset_id = self.next_item_id
            if bucket.save() and new_item.save() and self.save():
                bucket.items[new_item.asset_id] = new_item
                self.next_item_id += 1
                return self.save()
            else:
                return False
        return None

    def edit_asset(self,
                   asset_id=None,
                   name=None,
                   description=None,
                   item=None,
                   done=None,
                   buc_id=None):
        """Edit assets(item/bucket) on Profile.

        Args:
            name(str): new name of the item/bucket
            description(str):new description of item
            asset_id(int): asset_id for bucket/item
            item(bool):Specify whether asset is an item or bucket

        Returns:
            True if succesfull, False if item was not saved and None if the
            bucket does not exist.
        """
        if item and (buc_id or buc_id == 0):
            return self._edit_item(asset_id, name, description, done, buc_id)
        elif not item:
            return self._edit_bucket(asset_id, name)

    def _edit_item(self,
                   asset_id=None,
                   name=None,
                   description=None,
                   done=None,
                   buc_id=None):
        edit_item = self.get_item(item_id=asset_id, buc_id=buc_id)

        if edit_item:
            bucket = self.get_bucket(id=edit_item.bucket_id)
            if name and bucket:
                # bucket.items[name] = bucket.items.pop(edit_item.name)
                bucket.items[edit_item.asset_id].name = name
            if description and bucket:
                bucket.items[edit_item.asset_id].description = description
            if done is not None and bucket:
                bucket.items[edit_item.asset_id].done = done
            if bucket:
                return edit_item.save() and self.save() and bucket.save()
        return None

    def _edit_bucket(self, asset_id=None, name=None):
        edit_bucket = self.get_bucket(bucket_id=asset_id)
        if name and edit_bucket:
            # self.bucket_lists[name] = self.bucket_lists.pop(edit_bucket.name)
            edit_bucket.name = name
            return edit_bucket.save() and self.save()
        return None

    def delete_asset(self, asset_id=None, name=None, item=False, buc_id=None):
        """Delete an assets(item/bucket) on Profile.

        Args:
            name(str): Name of the item/bucket
            asset_id(int): Specify asset's id on profile
            item(bool): Specify whether asset is bucket or item

        Returns:
            True if succesfull, False if item was not deleted and None if the
            bucket/item does not exist.
        """
        assert_to_delete = None
        if item and (asset_id or asset_id == 0) and (buc_id or buc_id == 0):
            assert_to_delete = self.get_item(item_id=asset_id, buc_id=buc_id)
        elif item and name:
            assert_to_delete = self.get_item(name=name)
        elif asset_id or asset_id == 0:
            assert_to_delete = self.get_bucket(bucket_id=asset_id)
        elif name and not item:
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
