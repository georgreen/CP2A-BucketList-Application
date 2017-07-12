from unittest import TestCase

from app.base import database, new_app
from app.models import bucketlist, profile, user


class BaseTestCase(TestCase):
    def setUp(self):
        self.app = new_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        database.drop_all()
        database.create_all()

        self.registerdata = {
            "username": "Friedrich Nietzscher",
            "email": "Nietzschern@gmail.com",
            "password": "Userpassword#2345"
        }

        self.new_user = user.User(
            username="crimson",
            password="Userpassword#2345",
            email="crimson@gmail.com")

        self.data = {
            "email": "crimson@gmail.com",
            "password": "Userpassword#2345"
        }
        self.new_user.save()
        self.new_mentor = user.User("Turing", "Inigma1#UKT", "allan@gmail.com")
        self.new_mentor.save()
        self.new_follower = user.User("Knuth", "Log2#XUKT", "donald@gmail.com")

        self.testprofile = profile.Profile("@mentor", self.new_mentor)
        self.testprofile.save()
        self.new_bucket = bucketlist.Bucket("Travelling")
        self.new_bucket.profile_id = self.testprofile.id
        self.new_bucket.asset_id = 0
        self.new_bucket.save()

        self.new_item = bucketlist.Item("Drink alchol")
        self.new_item.profile_id = self.testprofile.id
        self.new_item.asset_id = 0
        self.new_item.bucket_id = self.new_bucket.id
        self.new_item.save()
        self.new_item1 = bucketlist.Item("Go to Mombasa")
        self.new_item1.profile_id = self.testprofile.id
        self.new_item1.asset_id = 1
        self.new_item1.bucket_id = self.new_bucket.id
        self.new_item1.save()

        # mock bucket
        self.new_bucket.items[self.new_item.asset_id] = self.new_item
        self.new_bucket.items[self.new_item1.asset_id] = self.new_item1
        self.new_bucket.save()

        # mock profile
        self.new_profile = profile.Profile("@crimson_profile", self.new_user)
        self.new_profile.save()
        self.new_profile.add_bucket("Travelling")
        self.new_profile.add_item(name="Drink alchol", buc_name="Travelling")
        self.new_profile.add_item(name="Go to Mombasa", buc_id=0)
        self.new_profile.mentors[self.new_mentor.username] = self.new_mentor
        self.new_profile.save()

        self.client = self.app.test_client()
        self.login_url = "/api/v1.0/login/"
        self.register_url = "/api/v1.0/register/"

    def tearDown(self):
        database.session.remove()
        database.drop_all()
        self.app_context.pop()
