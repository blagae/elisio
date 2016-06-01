""" tests for the frontend """
import unittest
from Elisio.utils import set_django

set_django()

from django.test import Client

class TestWeb(unittest.TestCase):
    """ tests for the frontend """
    #client = None

    def setUp(self):
        self.client = Client()

    def test_web_root_exists(self):
        """ This test acts as the canary in the coal mine for the web frontend
        If anything goes wrong with file imports, url dispatching,
        template loading, etc
        then the website is down and this test should fail
        """
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        
    def test_go(self):
        from Elisio.batchjob import find_all_verses_containing as find
        print(len(find('^uolu.*$', False)))