"""This module contains unit tests for models used in application."""

from app.models import bucketlist, profile, user
from tests.base_test_setup import BaseTestCase


class TestUser(BaseTestCase):
    def test_create_user(self):
        new_user = user.User("new_name", "user_password", "email@gmail.com")
        save = new_user.save()
        self.assertTrue(save)

        user_created = user.User.get_users()
        self.assertTrue(len(user_created) > 0)
        self.assertTrue(new_user in user_created)

        # create user using json_schema
        dict_data = {
            'username': 'geogreen123',
            'password': 'A123#445678q1000',
            'email': 'geogreen123@some.com'
        }
        schema = user.UserSchema()
        new_user, error = schema.load(dict_data)
        self.assertFalse(error)
        new_user.save()
        self.assertTrue(new_user in user.User.get_users())

    def test_schema_catch_invlaid_email(self):
        schema = user.UserSchema()
        # email
        dict_data = {
            'username': 'geogreen123',
            'password': 'A123#445678q1000',
            'email': ''
        }
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

        dict_data = {'username': 'geogreen123', 'password': 'A123#445678q1000'}
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

        dict_data = {
            'username': 'geogreen123',
            'password': 'A123#445678q1000',
            'email': "wrongemailfromat"
        }
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

    def test_schema_catch_invlaid_password(self):
        # missing capital leter
        dict_data = {
            'username': 'geogreen123',
            'password': '123#445678q1000',
            'email': 'geogreen123@some.com'
        }
        schema = user.UserSchema()
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

        # missing lower case letter
        dict_data = {
            'username': 'geogreen123',
            'password': 'A123#4456781000',
            'email': 'geogreen123@some.com'
        }
        schema = user.UserSchema()
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

        # missing specail characters
        dict_data = {
            'username': 'geogreen123',
            'password': '123445678q1000',
            'email': 'geogreen123@some.com'
        }
        schema = user.UserSchema()
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

        # less than 10 chracters
        dict_data = {
            'username': 'geogreen123',
            'password': '123#4',
            'email': 'geogreen123@some.com'
        }
        schema = user.UserSchema()
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

    def test_schema_catch_invlaid_username(self):
        # contains funny charactes
        dict_data = {
            'username': 'geogreen@####',
            'password': 'A123#445678q1000',
            'email': 'geogreen123@some.com'
        }
        schema = user.UserSchema()
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

        # empty
        dict_data = {
            'username': '',
            'password': 'A123#445678q1000',
            'email': 'geogreen123@some.com'
        }
        schema = user.UserSchema()
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

        # less than three characters
        dict_data = {
            'username': 'ge',
            'password': 'A123#445678q1000',
            'email': 'geogreen123@some.com'
        }
        schema = user.UserSchema()
        new_user, error = schema.load(dict_data)
        self.assertTrue(error)

    def test_edit_user(self):
        new_user = user.User("test_user", "user_password", "email@gmail.com")
        new_user.save()

        user_to_update = user.User.get_user(name="test_user")
        user_to_update.username = "update_username"
        user_to_update.email = "new_email@gmail.com"
        user_to_update.user_password = "new_password"
        user_to_update.save()

        deleted_user = user.User.get_user(name="test_user")
        self.assertEqual(deleted_user, None)
        updated_user = user.User.get_user(email="new_email@gmail.com")
        self.assertTrue(updated_user.username == "update_username")
        self.assertFalse(updated_user.authenticate_password("user_password"))
        self.assertTrue(updated_user.authenticate_password("new_password"))

    def test_delete_user(self):
        existing_user = user.User.get_user(name="crimson")
        self.assertTrue(existing_user)
        self.assertTrue(existing_user.username == "crimson")
        existing_user.delete()

        deleted_user = user.User.get_user(name="crimson")
        self.assertFalse(deleted_user)
        existing_users = user.User.get_users()
        self.assertNotIn(existing_user, existing_users)

    def test_query_non_existing_user(self):
        number_of_users = user.User.get_user(name="doesnotexist")
        self.assertEqual(number_of_users, None)

    def test_query_by_id(self):
        query = user.User.get_user(id=1)
        self.assertTrue(query == self.new_user)

        # query non-existing id
        query = user.User.get_user(id=8)
        self.assertFalse(query)

    def test_query_by_email(self):
        query = user.User.get_user(email="crimson@gmail.com")
        self.assertTrue(query.email == "crimson@gmail.com")
        self.assertTrue(query == self.new_user)

        # query non-existin email
        query = user.User.get_user(email="doesnotexist@gmail.com")
        self.assertFalse(query)

    def test_hashed_password_not_same_to_password(self):
        new_user = user.User(
            username="Manu", email="manu@someone", password="uniquekey")
        save = new_user.save()
        self.assertTrue(save)
        self.assertTrue(new_user.password != "uniquek")

    def test_password_property_not_readebale(self):
        with self.assertRaises(AttributeError):
            self.new_user.user_password

    def test_password_hash_is_unique_for_password(self):
        new_user = user.User(
            username="Manu", email="manu@someone", password="uniquekey")
        new_user.save()
        self.assertFalse(new_user.password == self.new_user.password)

    def test_authenticate_password_works(self):
        new_user = user.User(
            username="Manu", email="manu@someone", password="uniquekey")
        new_user.save()
        self.assertTrue(new_user.authenticate_password("uniquekey"))
        self.assertFalse(new_user.authenticate_password("wrongpassword"))

    def test_save_duplicate_users(self):
        new_user = user.User(
            username="Manu", email="manu@someone", password="uniquekey")
        new_user.save()

        new_user = user.User(
            username="Manu", email="manu@someone", password="uniquekey")
        self.assertFalse(new_user.save())

    def test_delete_non_existing_user(self):
        new_user = user.User(
            username="Manu", email="manu@someone", password="uniquekey")
        self.assertFalse(new_user.delete())
