import os
import unittest
from kiln.db import DEV_DB, connect


@unittest.skipUnless(os.path.exists(DEV_DB), "no data/dev.db (SETUP.md step 2)")
class TestDevDb(unittest.TestCase):
    def test_sample_data(self):
        self.assertGreater(connect().execute("SELECT COUNT(*) FROM firings").fetchone()[0], 0)
