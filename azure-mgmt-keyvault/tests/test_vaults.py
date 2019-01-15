from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
import azure.mgmt.keyvault.models

class MgmtKeyVaultTest(AzureMgmtTestCase):
    def setUp(self):
        super(MgmtKeyVaultTest, self).setUp()
        self.keyvault_client = self.create_mgmt_client(
            azure.mgmt.keyvault.KeyVaultManagementClient
        )

    @ResourceGroupPreparer()
    def test_vaults_operations(self, resource_group, **kwargs):
        account_name = self.get_resource_name('pykv')

        vault = self.keyvault_client.vaults.create_or_update(
            resource_group.name,
            account_name,
            {
                'location': self.region,
                'properties': {
                    'sku': {
                        'name': 'standard'
                    },
                    # Fake random GUID
                    'tenant_id': '6819f86e-5d41-47b0-9297-334f33d7922d',
                    'access_policies': []
                }
            }
        ).result()
        self.assertEqual(vault.name, account_name)

        vault = self.keyvault_client.vaults.get(
            resource_group.name,
            account_name
        )
        self.assertEqual(vault.name, account_name)

        vaults = list(self.keyvault_client.vaults.list_by_resource_group(resource_group.name))
        self.assertEqual(len(vaults), 1)
        self.assertIsInstance(vaults[0], azure.mgmt.keyvault.models.Vault)
        self.assertEqual(vaults[0].name, account_name)

        vaults = list(self.keyvault_client.vaults.list())
        self.assertGreater(len(vaults), 0)
        self.assertTrue(all(isinstance(v, azure.mgmt.keyvault.models.Resource) for v in vaults))

        self.keyvault_client.vaults.delete(
            resource_group.name,
            account_name
        )