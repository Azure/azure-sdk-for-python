from azure_devtools.scenario_tests import GeneralNameReplacer
from devtools_testutils import AzureMgmtTestCase
from azure.keyvault.secrets import SecretClient


class KeyvaultTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(KeyvaultTestCase, self).setUp()


    def tearDown(self):
        super(KeyvaultTestCase, self).tearDown()



