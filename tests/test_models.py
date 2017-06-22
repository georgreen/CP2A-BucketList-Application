from app.models import bucketlist, user
from tests.base_test_setup import BaseTestCase


class TestUser(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)

    def test_create_user(self):
        new_user = user.User("new_name", "password", "email@gmail.com")
        new_user.save()

        user_created = user.User.query.all()
        self.assertTrue(len(user_created) > 0)
        self.assertTrue(new_user in user_created)

    def test_edit_user(self):
        new_user = user.User("test_user", "password", "email@gmail.com")
        new_user.save()

        user_to_update = user.User.get_user(name="test_user")
        user_to_update.user_name = "update_user_name"
        user_to_update.email = "new_email@gmail.com"
        user_to_update.password = "new_password"
        user_to_update.save()

        number_of_users = user.User.get_user(name="test_user")
        self.assertEqual(number_of_users, None)
        updated_user = user.User.get_user(email="new_email@gmail.com")
        self.assertTrue(updated_user.user_name == "update_user_name")

    def test_delete_user(self):
        existing_user = user.User.get_user(name="crimson")
        self.assertTrue(existing_user)
        self.assertTrue(existing_user.user_name == "crimson")
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
        item = item = bucketlist.Item.get_item(name="Drink alchol")

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
        new_name = bucketlist.Bucket.get_bucket("Finally we edit it").name

        self.assertTrue(new_name == "Finally we edit it")

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


class TestProfile(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)

    def test_create_Profile(self):
        person_profile = user.Profile("@johndoe_profile")
        person_profile.save()

        query = user.Profile.get_profile(handle="@johndoe_profile")
        self.assertTrue(query)
        self.assertTrue(query.bucket_lists == {})
        self.assertTrue(query.mentors == {})
        self.assertTrue(query.handle == "@johndoe_profile")
        self.assertTrue(query.status == "SELBSTÜBERWINDUNG")

    def test_delete_Profile(self):
        query = user.Profile.get_profile(handle="@crimson_profile")
        self.assertTrue(query)

        query.delete()
        query = user.Profile.get_profile(handle="@crimson_profile")
        profiles = user.Profile.get_profiles()
        self.assertTrue(query not in profiles)

    def test_update_info(self):
        query = user.Profile.get_profile(handle="@crimson_profile")
        query.handle = "@eliforp_nosmirc"
        query.save()

        query = user.Profile.get_profile(handle="@eliforp_nosmirc")
        self.assertTrue(query)
        query = user.Profile.get_profile(handle="@crimson_profile")
        self.assertFalse(query)

    def test_query_by_info(self):
        new_profile = user.Profile(handle="@new_profile")
        new_profile.save()

        query = user.Profile.get_profile(handle="@new_profile")
        self.assertTrue(query.handle == "@new_profile")
