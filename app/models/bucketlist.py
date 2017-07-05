"""This module contains Modlels for Item and Bucketlist."""

from sqlalchemy.orm.collections import attribute_mapped_collection

from app.base import BaseModel, database


class Base(database.Model, BaseModel):
    """Base Configuration for Item and Bucket model.

    Implements common properties and methods in the models.
    """

    __abstract__ = True
    id = database.Column(database.Integer, primary_key=True)
    asset_id = database.Column(database.Integer)
    name = database.Column(database.String(128), nullable=False, unique=True)
    date_created = database.Column(
        database.DateTime, default=database.func.now())

    date_modified = database.Column(
        database.DateTime,
        default=database.func.now(),
        onupdate=database.func.now())

    @classmethod
    def get_object(cls, name=None, id=None, asset_id=None):
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
        elif id or id == 0:
            return cls.query.filter_by(id=id).first()
        elif asset_id or asset_id == 0:
            return cls.query.filter_by(asset_id=asset_id).first()
        else:
            return cls.query.all()


class Bucket(Base):
    """Model Bucket that holds items in the application."""

    __tablename__ = "buckets"
    items = database.relationship(
        "Item",
        collection_class=attribute_mapped_collection('name'),
        cascade="all, delete-orphan")

    created_by = database.Column(database.String(128))

    profile_id = database.Column(database.Integer,
                                 database.ForeignKey('profiles.id'))

    def __init__(self, name=""):
        """Initialize a bucket with it's name."""
        self.name = name

    def to_dict(self):

        return dict(
            name=self.name,
            profile_id=self.profile_id,
            id=self.asset_id,
            items={key: self.items[key].to_dict()
                   for key in self.items},
            created_by=self.created_by,
            date_created=str(self.date_created),
            date_modified=str(self.date_modified))

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
    def get_bucket(cls, name=None, id=None, asset_id=None, profile_id=None):
        """Get a buckets from the table buckets.

        Args:
            cls(Bucket): Model to be queried
            name(str) : name of bucket to be queried
            id(int): id for bucket to be queried

        Returns:
            list of buckets from the table
        """
        bucket = None
        if name:
            bucket = Bucket.get_object(name=name)
        elif id or id == 0:
            bucket = Bucket.get_object(id=id)
        elif asset_id or asset_id == 0:
            bucket = Bucket.get_object(asset_id=asset_id)

        if (profile_id or profile_id == 0) and bucket:
            if not (profile_id == bucket.profile_id):
                bucket = False
        return bucket


class Item(Base):
    """Model Item that represent todo experince in the application."""

    __tablename__ = "items"
    description = database.Column(database.String(256), default="my todo")
    done = database.Column(database.Boolean, default=False, nullable=False)

    bucket_id = database.Column(
        database.Integer, database.ForeignKey('buckets.id'), nullable=True)

    def __init__(self, name, description=""):
        """Initilize name and description for an item."""
        self.name = name
        self.description = description

    def to_dict(self):
        return dict(
            name=self.name,
            description=self.description,
            done=self.done,
            bucket_id=self.bucket_id,
            id=self.asset_id,
            date_created=str(self.date_created),
            date_modified=str(self.date_modified))

    @classmethod
    def get_item(cls, name=None, id=None, asset_id=None, profile_id=None):
        """Get an Item from the table items.

        Args:
            cls(Bucket): Model to be queried
            name(str) : name of bucket to be queried
            id(int): id for bucket to be queried

        Returns:
            an instance of Item if found in table, else None
        """
        item = None
        if name:
            item = cls.get_object(name=name)
        elif id or id == 0:
            item = cls.get_object(id=id)
        elif asset_id or asset_id == 0:
            item = cls.get_object(asset_id=asset_id)

        if (profile_id or profile_id == 0) and item:
            if not (profile_id == item.bucket_id):
                item = False
        return item
