"""This module contains Model for  a User."""

import re

from marshmallow import ValidationError, fields, validates
from werkzeug.security import check_password_hash, generate_password_hash

from app.base import BaseModel, database, json_schema


class User(database.Model, BaseModel):
    """Model Users that interact with the application."""

    __tablename__ = "users"
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(
        database.String(128), unique=True, nullable=False)
    password = database.Column(
        database.String(256), nullable=False, unique=False)
    email = database.Column(database.String(64), nullable=False, unique=True)
    date_created = database.Column(
        database.DateTime, default=database.func.now())
    profile_id = database.Column(database.Integer,
                                 database.ForeignKey('profiles.id'))

    def __init__(self, username="", password="", email=""):
        """Initilize user object with required params."""
        self.username = username
        self.user_password = password
        self.email = email

    @property
    def user_password(self):
        """Propery user_password."""
        raise AttributeError("Read operation Not allowed on user_password.")

    @user_password.setter
    def user_password(self, password):
        """Property setter for password."""
        self.password = generate_password_hash(str(password))

    def authenticate_password(self, password):
        """Validate user password.

        Args:
            password(str): User password

        Returns:
            instance of True if password match, else False
        """
        return check_password_hash(self.password, str(password))

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
            return cls.query.filter_by(username=name).first()
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


class UserSchema(json_schema.ModelSchema):
    """Define schema that can be used to serialize and deserialized User model.

    Provide Utilities to convert User object into a dictionary object or a
    dictionary object to a User object.
    """

    class Meta:
        """Define meta class for UserSchema."""

        model = User

    email = fields.Email(required=True)

    @validates('username')
    def validate_username(self, value):
        """Username validator check if user name is valid."""
        if value == "":
            raise ValidationError("User name can not be empty.")
        elif not re.match("^[A-Za-z0-9]+\s?[A-Za-z0-9]+$", value):
            raise ValidationError("Username can not have special characters.")
        elif not 3 < len(value) < 128:
            raise ValidationError("Username should contain 3 or more letters.")

    @validates('password')
    def validate_password(self, value):
        """Password validator check if user password is valid."""
        if value == "":
            raise ValidationError("user_password can not be empty")
        elif len(value) < 8:
            raise ValidationError(
                "password is too short, must contain more than 8 characters")
        elif not re.match(
                "((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%*&]).{7,56})",
                value):
            raise ValidationError(
                "must contains one digit 0-9, one lowercase characters, one " +
                "uppercase characters, one special symbols in the list *&@#$%")
