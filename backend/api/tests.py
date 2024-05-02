from http import HTTPStatus

from django.test import TestCase
from rest_framework.test import APIClient


class CatsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_exists(self):
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
