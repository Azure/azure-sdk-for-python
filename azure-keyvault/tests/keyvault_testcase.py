from azure_devtools.scenario_tests import GeneralNameReplacer
from devtools_testutils import AzureMgmtTestCase
from azure.keyvault import KeyVaultClient, KeyVaultAuthentication, AccessToken


class KeyvaultTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(KeyvaultTestCase, self).setUp()
        self.list_test_size = 2
        if self.is_live:
            self.client = self.create_basic_client(KeyVaultClient)
        else:

            def _auth_callback(server, resource, scope):
                return AccessToken('Bearer', 'fake-token')
            self.client = KeyVaultClient(KeyVaultAuthentication(authorization_callback=_auth_callback))

    def tearDown(self):
        super(KeyvaultTestCase, self).tearDown()


