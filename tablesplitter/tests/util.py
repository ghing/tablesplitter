from unittest import TestCase

from tablesplitter.util import slugify

class UtilTestCase(TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("Mississippi Election Results"),
                         "mississippi-election-results")
