"""This module contains unit tests for models used in application."""

from app.models import bucketlist, profile, user
from tests.base_test_setup import BaseTestCase


class TestUser(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)

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
            'username': 'geo',
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


class TestItem(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)

    def test_create_Item(self):
        item = bucketlist.Item(
            "swimming accross the sea",
            description=""" I Will go swimming
                               across the red sea
                               one day, i say one day i will
                               """)
        item.save()
        query = bucketlist.Item.get_item(name="swimming accross the sea")
        self.assertTrue(query)
        self.assertEqual(item, query)

    def test_update_item(self):
        item = bucketlist.Item("I will go to school")
        item.save()

        query = bucketlist.Item.get_item(name="I will go to school")
        query.name = "I will not go to school"
        query.description = "Get some basic education"
        query.save()

        query = bucketlist.Item.get_item(name="I will not go to school")
        self.assertTrue(query)
        self.assertTrue(query.description == "Get some basic education")
        query = bucketlist.Item.get_item(name="I will go to school")
        self.assertFalse(query)

    def test_delete_item(self):
        item = bucketlist.Item.get_item(name="Drink alchol")
        self.assertTrue(item)
        item.delete()
        item = bucketlist.Item.get_item(name="Drink alchol")

        self.assertFalse(item)

    def test_query_non_existing_item(self):
        item = bucketlist.Item.get_item(name="Doesnotexist")
        self.assertFalse(item)

    def test_query_by_id(self):
        item = bucketlist.Item("I will go to Mombasa")
        item.save()

        query = bucketlist.Item.get_item(id=item.id)
        self.assertTrue(item == query)

        # query non-existin id
        item = bucketlist.Item.get_item(id=1400)
        self.assertFalse(item)

    def test_query_by_name(self):
        item = bucketlist.Item(name="new item in list")
        item.save()

        query = bucketlist.Item.get_item(name="new item in list")
        self.assertTrue(query)

        # query non-exsting name
        query = bucketlist.Item.get_item(name="item does not exist")
        self.assertFalse(query)

    def test_save_duplicate_items(self):
        item = bucketlist.Item(name="new item in list")
        item.save()

        item = bucketlist.Item(name="new item in list")
        self.assertFalse(item.save())

    def test_delete_non_existing_Item(self):
        item = bucketlist.Item(name="new item in list")
        self.assertFalse(item.delete())


class TestBucket(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)

    def test_create_Bucket(self):
        bucket = bucketlist.Bucket("Movies to watch")
        saved = bucket.save()
        self.assertTrue(saved)

        buckets = bucketlist.Bucket.get_buckets()
        self.assertTrue(len(buckets) > 0)
        self.assertIn(bucket, buckets)

    def test_delete_bucket(self):
        buckets = bucketlist.Bucket.get_buckets()
        number_current_buckets = len(buckets)
        bucket = bucketlist.Bucket.get_bucket(name="Travelling")
        deleted = bucket.delete()

        self.assertTrue(deleted)
        number_of_after_del_buckets = len(bucketlist.Bucket.get_buckets())
        self.assertTrue(number_current_buckets > number_of_after_del_buckets)
        buckets = bucketlist.Bucket.get_buckets()
        self.assertNotIn(bucket, buckets)

    def test_update_bucket(self):
        test_bucket = bucketlist.Bucket("typo in nammme")
        test_bucket.save()

        bucket_to_update = bucketlist.Bucket.get_bucket("typo in nammme")
        bucket_to_update.name = "Finally we edit it"
        bucket_to_update.save()
        query = bucketlist.Bucket.get_bucket("Finally we edit it")

        self.assertTrue(query.name == "Finally we edit it")

    def test_query_non_existing_Bucket(self):
        bucket = bucketlist.Bucket.get_bucket(name="Doesnotexist bucket")
        self.assertFalse(bucket)

    def test_query_bucket_by_id(self):
        bucket = bucketlist.Bucket("Bucketd")
        bucket.save()

        bucket1 = bucketlist.Bucket.get_bucket(id=bucket.id)
        self.assertTrue(bucket == bucket1)

        # query non-existing bucket
        bucket2 = bucketlist.Bucket.get_bucket(id=500)
        self.assertFalse(bucket2)

    def test_query_bucket_by_name(self):
        bucket = bucketlist.Bucket("New Experinces")
        bucket.save()

        bucket1 = bucketlist.Bucket.get_bucket(name=bucket.name)
        self.assertTrue(bucket == bucket1)

        # query non-existing bucket
        bucket1 = bucketlist.Bucket.get_bucket(name="Doesnot")
        self.assertFalse(bucket1)

    def test_save_duplicate_buckets(self):
        bucket = bucketlist.Bucket("New Experinces")
        bucket.save()

        bucket = bucketlist.Bucket("New Experinces")
        self.assertFalse(bucket.save())

    def test_delete_non_existing_bucket(self):
        bucket = bucketlist.Bucket("New Experinces")
        self.assertFalse(bucket.delete())


class TestProfile(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)

    def test_create_Profile(self):
        person_profile = profile.Profile("@johndoe_profile", self.new_user)
        person_profile.save()

        query = profile.Profile.get_profile(handle="@johndoe_profile")
        self.assertTrue(query)
        self.assertTrue(query.bucket_lists == {})
        self.assertTrue(query.mentors == {})
        self.assertTrue(query.handle == "@johndoe_profile")
        self.assertTrue(query.status == "SELBSTÜBERWINDUNG")

    def test_delete_Profile(self):
        query = profile.Profile.get_profile(handle="@crimson_profile")
        self.assertTrue(query)

        delete = query.delete()
        self.assertTrue(delete)
        query1 = profile.Profile.get_profile(handle="@crimson_profile")
        self.assertFalse(query1)
        profiles = profile.Profile.get_profiles()
        self.assertTrue(query not in profiles)

    def test_update_info(self):
        query = profile.Profile.get_profile("@crimson_profile")
        query.handle = "@eliforp_nosmirc"
        query.save()

        query = profile.Profile.get_profile(handle="@eliforp_nosmirc")
        self.assertTrue(query)
        query = profile.Profile.get_profile(handle="@crimson_profile")
        self.assertFalse(query)

    def test_query_by_info(self):
        new_profile = profile.Profile("@new_profile", self.new_follower)
        new_profile.save()

        query = profile.Profile.get_profile(handle="@new_profile")
        self.assertTrue(query.handle == "@new_profile")

    def test_create_item_on_profile(self):
        saved = self.new_profile.add_item(
            name="Go to Limuru", buc_name="Travelling")
        self.assertTrue(saved)
        query = bucketlist.Item.get_item(name="Go to Limuru")
        self.assertTrue(query.name == "Go to Limuru")

    def test_create_bucket_on_profile(self):
        saved = self.new_profile.add_bucket("Space")
        self.assertTrue(saved)
        query = bucketlist.Bucket.get_bucket(name="Space")
        self.assertTrue(query.name == "Space")

    def test_get_item_from_profile(self):
        item = self.new_profile.get_item(name="Go to Mombasa")
        self.assertTrue(item.name == "Go to Mombasa")
        self.assertTrue(item)

        item = self.new_profile.add_item(
            "Testing search by asertNo", buc_name="Travelling")
        item = self.new_profile.get_item(name="Testing search by asertNo")

        item = self.new_profile.get_item(item_id=item.asset_id)
        self.assertTrue(item)

    def test_get_bucket_from_profile(self):
        bucket = self.new_profile.get_bucket(name="Travelling")
        self.assertTrue(bucket.name == "Travelling")

    def test_edit_assert_on_profilr(self):
        # add item
        self.new_profile.add_item(
            "Vist muny places", description="Rwanda", buc_name="Travelling")

        # edit
        item = self.new_profile.get_item(name="Vist muny places")

        edit = self.new_profile.edit_asset(
            item=True,
            asset_id=item.asset_id,
            name="Vist many places",
            description="congo, rwanda, uganda")
        #import pdb
        #pdb.set_trace()
        self.assertTrue(edit)
        item = self.new_profile.get_item(name="Vist muny places")
        self.assertFalse(item)
        item = self.new_profile.get_item(name="Vist many places")
        self.assertTrue(item)

        # add bucket
        self.new_profile.add_bucket("Philosophyyyyyyy")
        bucket = self.new_profile.get_bucket(name="Philosophyyyyyyy")
        # edit
        edit = self.new_profile.edit_asset(
            item=False, name="Philosophy", asset_id=bucket.asset_id)
        self.assertTrue(edit)
        bucket = self.new_profile.get_bucket(name="Philosophyyyyyyy")
        self.assertFalse(bucket)
        bucket = self.new_profile.get_bucket(name="Philosophy")
        self.assertTrue(bucket)

    def test_delete_on_profile(self):
        deleted = self.new_profile.delete_asset(name="Drink alchol", item=True)
        self.assertTrue(deleted)
        query = bucketlist.Item.get_item(name="Drink alchol")
        self.assertFalse(query)

        deleted = self.new_profile.delete_asset(name="Travelling", item=False)
        self.assertTrue(deleted)
        query = bucketlist.Bucket.get_bucket(name="Travelling")
        self.assertFalse(query)
