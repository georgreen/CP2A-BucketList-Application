"""This module contains unit tests for models used in application."""

from app.models import bucketlist, profile, user
from tests.base_test_setup import BaseTestCase


class TestProfile(BaseTestCase):
    def test_create_Profile(self):
        person_profile = profile.Profile("@johndoe_profile", self.new_user)
        person_profile.save()

        query = profile.Profile.get_profile(handle="@johndoe_profile")
        self.assertTrue(query)
        self.assertTrue(query.bucket_lists == {})
        self.assertTrue(query.mentors == {})
        self.assertTrue(query.handle == "@johndoe_profile")
        self.assertTrue(query.status == "SELBSTUBERWINDUNG")

    def test_delete_Profile(self):
        query = profile.Profile.get_profile(handle="@crimson_profile")
        owner = query.owner
        self.assertTrue(query and owner)

        delete = query.delete()
        self.assertTrue(delete)
        query1 = profile.Profile.get_profile(handle="@crimson_profile")
        self.assertFalse(query1)
        profiles = profile.Profile.get_profiles()
        self.assertTrue(query not in profiles)

        deleted_user = user.User.get_user(name=owner.username)
        self.assertFalse(deleted_user)

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
        query = bucketlist.Item.get_item(
            name="Go to Limuru", profile_id=self.new_profile.id)
        self.assertTrue(query.name == "Go to Limuru")

    def test_create_bucket_on_profile(self):
        saved = self.new_profile.add_bucket("Space")
        self.assertTrue(saved)
        query = bucketlist.Bucket.get_bucket(
            name="Space", profile_id=self.new_profile.id)
        self.assertTrue(query.name == "Space")

    def test_get_item_from_profile(self):
        item = self.new_profile.get_item(name="Go to Mombasa")
        self.assertTrue(item.name == "Go to Mombasa")
        self.assertTrue(item)

        item = self.new_profile.add_item(
            "Testing search by asertNo", buc_name="Travelling")
        item = self.new_profile.get_item(name="Testing search by asertNo")

        item = self.new_profile.get_item(item_id=item.asset_id, buc_id=0)
        self.assertTrue(item)

    def test_get_bucket_from_profile(self):
        bucket = self.new_profile.get_bucket(name="Travelling")
        self.assertTrue(bucket.name == "Travelling")

    def test_edit_asset_on_profile(self):
        # add item
        self.new_profile.add_item(
            "Vist muny places", description="Rwanda", buc_name="Travelling")

        # edit
        item = self.new_profile.get_item(name="Vist muny places")

        edit = self.new_profile.edit_asset(
            item=True,
            asset_id=item.asset_id,
            name="Vist many places",
            description="congo, rwanda, uganda",
            buc_id=0)

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
