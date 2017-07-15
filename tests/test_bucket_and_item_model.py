"""This module contains unit tests for models used in application."""

from app.models import bucketlist
from tests.base_test_setup import BaseTestCase


class TestItem(BaseTestCase):
    def test_create_Item(self):
        item = bucketlist.Item(
            "swimming accross the sea",
            description=""" I Will go swimming
                               across the red sea
                               one day, i say one day i will
                               """)
        item.profile_id = self.testprofile.id
        item.save()
        query = bucketlist.Item.get_item(
            name="swimming accross the sea", profile_id=self.testprofile.id)
        self.assertTrue(query)
        self.assertEqual(item, query)

    def test_update_item(self):
        item = bucketlist.Item("I will go to school")
        item.profile_id = self.testprofile.id
        item.save()

        query = bucketlist.Item.get_item(
            name="I will go to school", profile_id=self.testprofile.id)
        query.name = "I will not go to school"
        query.description = "Get some basic education"
        query.save()

        query = bucketlist.Item.get_item(
            name="I will not go to school", profile_id=self.testprofile.id)
        self.assertTrue(query)
        self.assertTrue(query.description == "Get some basic education")
        query = bucketlist.Item.get_item(
            name="I will go to school", profile_id=self.testprofile.id)
        self.assertFalse(query)

    def test_delete_item(self):
        item = bucketlist.Item.get_item(
            name="Drink alchol", profile_id=self.testprofile.id)
        self.assertTrue(item)
        item.delete()
        item = bucketlist.Item.get_item(
            name="Drink alchol", profile_id=self.testprofile.id)

        self.assertFalse(item)

    def test_query_non_existing_item(self):
        item = bucketlist.Item.get_item(
            name="Doesnotexist", profile_id=self.testprofile.id)
        self.assertFalse(item)

    def test_query_by_id(self):
        item = bucketlist.Item("I will go to Mombasa")
        item.profile_id = self.testprofile.id
        item.save()

        query = bucketlist.Item.get_item(id=item.id)
        self.assertTrue(item == query)

        # query non-existin id
        item = bucketlist.Item.get_item(id=1400)
        self.assertFalse(item)

    def test_query_by_name(self):
        item = bucketlist.Item(name="new item in list")
        item.profile_id = self.testprofile.id
        item.save()

        query = bucketlist.Item.get_item(
            name="new item in list", profile_id=self.testprofile.id)
        self.assertTrue(query)

        # query non-exsting name
        query = bucketlist.Item.get_item(
            name="item does not exist", profile_id=self.testprofile.id)
        self.assertFalse(query)

    def test_save_duplicate_items(self):
        item = bucketlist.Item(name="new item in list")
        item.save()

        item = bucketlist.Item(name="new item in list")
        self.assertTrue(item.save())

    def test_delete_non_existing_Item(self):
        item = bucketlist.Item(name="new item in list")
        self.assertFalse(item.delete())


class TestBucket(BaseTestCase):
    def test_create_Bucket(self):
        bucket = bucketlist.Bucket("Movies to watch")
        bucket.profile_id = self.testprofile.id
        saved = bucket.save()
        self.assertTrue(saved)

        buckets = bucketlist.Bucket.get_buckets()
        self.assertTrue(len(buckets) > 0)
        self.assertIn(bucket, buckets)

    def test_delete_bucket(self):
        buckets = bucketlist.Bucket.get_buckets()
        number_current_buckets = len(buckets)
        bucket = bucketlist.Bucket.get_bucket(
            name="Travelling", profile_id=self.testprofile.id)
        deleted = bucket.delete()

        self.assertTrue(deleted)
        number_of_after_del_buckets = len(bucketlist.Bucket.get_buckets())
        self.assertTrue(number_current_buckets > number_of_after_del_buckets)
        buckets = bucketlist.Bucket.get_buckets()
        self.assertNotIn(bucket, buckets)

    def test_update_bucket(self):
        test_bucket = bucketlist.Bucket("typo in nammme")
        test_bucket.profile_id = self.testprofile.id
        test_bucket.save()

        bucket_to_update = bucketlist.Bucket.get_bucket(
            "typo in nammme", profile_id=self.testprofile.id)
        bucket_to_update.name = "Finally we edit it"
        bucket_to_update.save()
        query = bucketlist.Bucket.get_bucket(
            "Finally we edit it", profile_id=self.testprofile.id)

        self.assertTrue(query.name == "Finally we edit it")

    def test_query_non_existing_Bucket(self):
        bucket = bucketlist.Bucket.get_bucket(
            name="Doesnotexist bucket", profile_id=self.testprofile.id)
        self.assertFalse(bucket)

    def test_query_bucket_by_id(self):
        bucket = bucketlist.Bucket("Bucketd")
        bucket.profile_id = self.testprofile.id
        bucket.save()

        bucket1 = bucketlist.Bucket.get_bucket(id=bucket.id)
        self.assertTrue(bucket == bucket1)

        # query non-existing bucket
        bucket2 = bucketlist.Bucket.get_bucket(id=500)
        self.assertFalse(bucket2)

    def test_query_bucket_by_name(self):
        bucket = bucketlist.Bucket("New Experinces")
        bucket.profile_id = self.testprofile.id
        bucket.save()

        bucket1 = bucketlist.Bucket.get_bucket(
            name=bucket.name, profile_id=self.testprofile.id)
        self.assertTrue(bucket == bucket1)

        # query non-existing bucket
        bucket1 = bucketlist.Bucket.get_bucket(
            name="Doesnot", profile_id=self.testprofile.id)
        self.assertFalse(bucket1)

    def test_save_duplicate_buckets(self):
        bucket = bucketlist.Bucket("New Experinces")
        bucket.save()

        bucket = bucketlist.Bucket("New Experinces")
        self.assertTrue(bucket.save())

    def test_delete_non_existing_bucket(self):
        bucket = bucketlist.Bucket("New Experinces")
        self.assertFalse(bucket.delete())
