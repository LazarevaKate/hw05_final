from unittest import TestCase

from django.test import Client


class StaticURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()


def test_author(self):
    response = self.guest_client.get('/about/author')
    self.assertEqual(response.status_code, 200)


def test_tech(self):
    response = self.guest_client.get('/about/tech')
    self.assertEqual(response.status_code, 200)
