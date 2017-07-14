import json

import flask
from tests.base_test_setup import BaseTestCase


class TestLogin(BaseTestCase):
    def test_user_login(self):
        response = self.client.post(self.login_url, data=self.data)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)

        self.assertTrue(response.content_type == "application/json")

    def test_user_invalid_email(self):
        response = self.client.post(
            self.login_url,
            data=dict(email="crimson", password="password12345"))
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)

        self.assertTrue(response.content_type == "application/json")

    def test_user_wrong_password(self):
        response = self.client.post(
            self.login_url,
            data=dict(email="crimson@gmail.com", password="M1#mypassword"))
        self.assertTrue(response.status_code == 401)
        data = json.loads(response.data)

        self.assertTrue(response.content_type == "application/json")

    def test_empty_credentials(self):
        response = self.client.post(self.login_url, data=json.dumps({}))
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)

        self.assertTrue(response.content_type == "application/json")

        response = self.client.post(
            self.login_url, data=dict(email="crimson@gmail.com"))
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)

        self.assertTrue(response.content_type == "application/json")

    def test_wrong_login_url(self):
        response = self.client.post(
            "/auth/login/",
            data=dict(email="crimson@gmail.com", password="W#3rongpassword"))
        self.assertTrue(response.status_code == 404)

    def test_login_nonexisting_user(self):
        response = self.client.post(
            self.login_url,
            data=dict(
                email="nonexistinguser@gmail.com", password="M1#mypassword"))

        self.assertTrue(response.status_code == 401)
        data = json.loads(response.data)

        self.assertTrue(response.content_type == "application/json")

    def test_login_url_and_data(self):
        with self.app.test_request_context(self.login_url, data=self.data):
            self.assertTrue(flask.request.path == self.login_url)


class TestRegister(BaseTestCase):
    def test_user_register(self):
        response = self.client.post(self.register_url, data=self.registerdata)
        self.assertTrue(response.status_code == 201)

    def test_missing_data_register(self):
        bad_data = {
            "email": "Nietzschern@gmail.com",
            "password": "user_password#2345"
        }
        response = self.client.post(self.register_url, data=bad_data)
        self.assertTrue(response.status_code == 400)

        response = self.client.post(self.register_url, data={})
        self.assertTrue(response.status_code == 400)

    def test_register_existing_users(self):
        # sigup a new user with email
        existing_user = dict(
            username="crimson2",
            password="Userpassword#2345",
            email="crimson2@gmail.com")
        response = self.client.post(self.register_url, data=existing_user)
        self.assertTrue(response.status_code == 201)

        # singup existing user name
        existing_user = dict(
            username="crimson2",
            password="Userpassword#2345",
            email="crimson2@gmail.com")
        response = self.client.post(self.register_url, data=existing_user)
        self.assertTrue(response.status_code == 400)
