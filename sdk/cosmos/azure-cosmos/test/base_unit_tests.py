import unittest
import pytest
import azure.cosmos.base as base

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class BaseUnitTests(unittest.TestCase):
    def test_is_name_based(self):
        self.assertFalse(base.IsNameBased("dbs/xjwmAA==/"))
        
        # This is a database name that ran into 'Incorrect padding'
        # exception within base.IsNameBased function
        self.assertTrue(base.IsNameBased("dbs/paas_cmr"))
