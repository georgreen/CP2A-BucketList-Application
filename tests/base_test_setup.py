from unittest import TestCase

from flask import current_app

from app.base import database, new_app
from app.models import bucketlist, user


class BaseTestCase(TestCase):

    def setUp(self):
        self.app = new_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        database.create_all()

        self.new_user = user.User("crimson", "password", "crimson@gmail.com")
        self.new_user.save()
        self.new_mentor = user.User("Turing", "Inigma", "allan@gmail.com")
        self.new_mentor.save()
        self.new_follower = user.User("Knuth", "log2", "donald@gmail.com")

        self.new_bucket = bucketlist.Bucket("Travelling")
        self.new_bucket.save()

        self.new_item = bucketlist.Item("Drink alchol")
        self.new_item.save()
        self.new_item1 = bucketlist.Item("Go to Mombasa")
        self.new_item1.save()

        self.new_profile = user.Profile("@crimson_profile")
        self.new_profile.save()

        # Assemble all componets
        self.new_profile.owner = self.new_user
        self.new_bucket.items[self.new_item.name] = self.new_item
        self.new_bucket.items[self.new_item1.name] = self.new_item1
        self.new_bucket.save()
        self.new_profile.bucket_lists[self.new_bucket.name] = self.new_bucket
        self.new_profile.mentors[self.new_mentor.user_name] = self.new_mentor
        self.new_profile.save()
        self.client = self.app.test_client()

    def tearDown(self):
        database.session.remove()
        database.drop_all()
        self.app_context.pop()
