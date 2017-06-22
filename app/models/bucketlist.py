"""This module contains Modlels for Item and Bucketlist."""

from sqlalchemy.orm.collections import attribute_mapped_collection

from app.base import BaseModel, database, json_schema


class Base(database.Model, BaseModel):
    """Base Configuration for Item and Bucket model.

    Implements common properties and methods in the models.
    """

    __abstract__ = True
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(128), nullable=False, unique=True)
    date_created = database.Column(
        database.DateTime, default=database.func.now())

    date_modified = database.Column(
        database.DateTime,
        default=database.func.now(),
        onupdate=database.func.now())

    @classmethod
    def get_object(cls, name=None, id=None):
        """Query database using the specified param as a filter.

        Args:
            cls (Class): Specify table to be queried
            name (str): Specify name for the object to be queried
            id (int) : Specify id for the object to be queried

        Returns:
            An instance of the class passed in cls if succefull else None
        """
        if name:
            return cls.query.filter_by(name=name).first()
        elif id:
            return cls.query.filter_by(id=id).first()
        else:
            return cls.query.all()


class Bucket(Base):
    """Model Bucket that holds items in the application."""

    __tablename__ = "buckets"
    items = database.relationship(
        "Item",
        collection_class=attribute_mapped_collection('name'),
        cascade="all, delete-orphan")

    created_by = database.Column(
        database.String, database.ForeignKey('users.user_name'), nullable=True)

    profile_id = database.Column(database.Integer,
                                 database.ForeignKey('profiles.id'))

    def __init__(self, name=""):
        """Initialize a bucket with it's name."""
        self.name = name

    @classmethod
    def get_buckets(cls):
        """Get all buckets from the table buckets.

        Args:
            cls(Bucket): Model to be queried

        Returns:
            list of buckets from the table
        """
        return Bucket.get_object()

    @classmethod
    def get_bucket(cls, name=None, id=None):
        """Get a buckets from the table buckets.

        Args:
            cls(Bucket): Model to be queried
            name(str) : name of bucket to be queried
            id(int): id for bucket to be queried

        Returns:
            list of buckets from the table
        """
        if name:
            return Bucket.get_object(name=name)
        elif id:
            return Bucket.get_object(id=id)


class Item(Base):
    """Model Item that represent todo experince in the application."""

    __tablename__ = "items"
    description = database.Column(database.String(256), default="")
    done = database.Column(database.Boolean, default=False)

    bucket_id = database.Column(
        database.Integer, database.ForeignKey('buckets.id'), nullable=True)

    def __init__(self, name, description=""):
        """Initilize name and description for an item."""
        self.name = name
        self.description = description

    @classmethod
    def get_item(cls, name=None, id=None):
        """Get an Item from the table items.

        Args:
            cls(Bucket): Model to be queried
            name(str) : name of bucket to be queried
            id(int): id for bucket to be queried

        Returns:
            an instance of Item if found in table, else None
        """
        if name:
            return Item.get_object(name=name)
        elif id:
            return Item.get_object(id=id)


class ItemSchema(json_schema.ModelSchema):
    """Define schema to convert item instance to Dictionary object."""

    class Meta:
        model = Item


class BucketSchema(json_schema.ModelSchema):
    """Define schema to convert Bucket instance to Dictionary object."""

    class Meta:
        model = Bucket
