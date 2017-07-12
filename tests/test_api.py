import json

from tests.base_test_setup import BaseTestCase


class TestBucketList(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        response = self.client.post(self.login_url, data=self.data)
        self.token = json.loads(response.data)["token"]
        self.headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def tearDown(self):
        BaseTestCase.tearDown(self)

    def test_create_bucketlist(self):

        # create bucket
        data = json.dumps({"name": "hello world"})
        response = self.client.post(
            '/api/v1.0/bucketlist/', headers=self.headers, data=data)
        self.assertTrue(response.status_code == 201)
        data = json.loads(response.data)
        self.assertTrue(data['bucket'])
        self.assertTrue(data['bucket'].get('name') == "hello world")
        self.assertTrue(data['message'] == "bucket created succesfully")

    def test_get_one_bucketlist(self):
        response = self.client.get(
            '/api/v1.0/bucketlist/0', headers=self.headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue(data['bucket'])

    def test_get_many_bucketlist(self):
        response = self.client.get(
            '/api/v1.0/bucketlist/', headers=self.headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue(data['buckets'])
        self.assertTrue(isinstance(data['buckets'], dict))

    def test_edit_bucketlist(self):
        data = json.dumps({"name": "new name"})
        response = self.client.put(
            '/api/v1.0/bucketlist/0', headers=self.headers, data=data)
        self.assertTrue(response.status_code == 201)
        data = json.loads(response.data.decode())
        self.assertTrue(data['bucket'])
        self.assertTrue(data['bucket'].get('name') == "new name")
        self.assertTrue(data['message'] == "Updated bucket succesfully")

    def test_delete_buckelist(self):
        response = self.client.delete(
            '/api/v1.0/bucketlist/0', headers=self.headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue(data["message"] == "Bucket deleted succesfully")

    def test_create_item(self):
        data = json.dumps({
            "name": "new item",
            "description": "Testing new item"
        })
        response = self.client.post(
            "/api/v1.0/bucketlist/0/items", headers=self.headers, data=data)
        self.assertTrue(response.status_code == 201)
        data = json.loads(response.data)
        self.assertTrue(data["item"].get("id") == 2)

    def test_get_item(self):
        response = self.client.get(
            "/api/v1.0/bucketlist/0/items/0", headers=self.headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue(data['0'].get("item").get("id") == 0)

    def test_edit_item(self):
        data = json.dumps({
            "name": "new_name",
            "description": "new description"
        })
        response = self.client.put(
            "/api/v1.0/bucketlist/0/items/0", headers=self.headers, data=data)
        self.assertTrue(response.status_code == 201)
        data = json.loads(response.data)
        self.assertTrue(data['item'].get("id") == 0)
        self.assertTrue(data['item'].get("name") == "new_name")
        self.assertTrue(data['item'].get("description") == "new description")

    def test_delete_item(self):
        response = self.client.delete(
            "/api/v1.0/bucketlist/0/items/0", headers=self.headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue(data["message"] == "Item deleted succesfully")
