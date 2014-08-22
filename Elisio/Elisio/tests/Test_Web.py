import unittest
from Elisio.engine.verseProcessor import setDjango

setDjango()

from django.test import Client

class Test_Web(unittest.TestCase):
    client = None

    def setUp(self):
        client = Client()

    def test_WebRootExists(self):
        """ This test acts as the canary in the coal mine for the web frontend
        If anything goes wrong with file imports, url dispatching, template loading, etc
        then the website is down and this test should fail
        """
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)