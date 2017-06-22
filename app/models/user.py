"""This module contains Modlels for User and Profile."""

from sqlalchemy.orm.collections import attribute_mapped_collection

from app.base import BaseModel, database, json_schema

budy = database.Table('budys',
                      database.Column("user_id", database.Integer,
                                      database.ForeignKey('users.id')),
                      database.Column("profile_id", database.Integer,
                                      database.ForeignKey('profiles.id')))


class User(database.Model, BaseModel):
    """Model Users that interact with the application."""

    __tablename__ = "users"
    id = database.Column(database.Integer, primary_key=True)
    user_name = database.Column(database.String(128), unique=True)
    password = database.Column(database.String(256), nullable=False)
    email = database.Column(database.String(64), nullable=True, unique=True)
    date_created = database.Column(
        database.DateTime, default=database.func.now())
    profile_id = database.Column(database.Integer,
                                 database.ForeignKey('profiles.id'))

    def __init__(self, name, password, email=""):
        """Initilize user object with required params."""
        self.user_name = name
        self.password = password
        self.email = email

    @classmethod
    def get_user(cls, name=None, id=None, email=None):
        """Get a User from the table users.

        Args:
            cls (User): Model to be queried
            name (str): Specify name for user
            email (str): Specify email for user

        Returns:
            instance of User if succesfull, else None
        """
        if name:
            return cls.query.filter_by(user_name=name).first()
        elif email:
            return cls.query.filter_by(email=email).first()
        elif id:
            return cls.query.filter_by(id=id).first()
        return None

    @classmethod
    def get_users(cls):
        """Get all Users from the table users.

        Args:
            cls (User): Model to be queried

        Returns:
            list of all users
        """
        return cls.query.all()


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
        collection_class=attribute_mapped_collection('user_name'),
        backref=database.backref('followers'))

    bucket_lists = database.relationship(
        "Bucket",
        collection_class=attribute_mapped_collection('name'),
        cascade="all, delete-orphan")

    def __init__(self, handle=""):
        """Initilize the profile with required information."""
        self.handle = handle

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


class UserSchema(json_schema.ModelSchema):
    """Define schema to convert User instance to Dictionary object."""

    class Meta:
        model = User


class ProfileSchema(json_schema.ModelSchema):
    """Define schema to convert Profile instance to Dictionary object."""

    class Meta:
        model = Profile
