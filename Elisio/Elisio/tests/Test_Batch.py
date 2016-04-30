""" tests for the batch processes """
import unittest

class TestBatch(unittest.TestCase):
    def test_create_xml(self):
        """ creates XML with some data """
        from Elisio.batchjob import fill_tree
        fill_tree()
