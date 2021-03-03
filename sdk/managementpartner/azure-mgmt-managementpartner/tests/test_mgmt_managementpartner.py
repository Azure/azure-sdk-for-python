from azure.mgmt.managementpartner import ACEProvisioningManagementPartnerAPI
from azure.mgmt.managementpartner.models import PartnerResponse
from devtools_testutils import AzureMgmtTestCase
import unittest


unittest.skip("skip test")
class MgmtPartnerTest(AzureMgmtTestCase):

    def _validate_partner(self, PartnerResponse):
        self.assertIsNotNone(PartnerResponse)
        self.assertIsNotNone(PartnerResponse.id)
        self.assertIsNotNone(PartnerResponse.name)
        self.assertIsNotNone(PartnerResponse.partner_id)
        self.assertIsNotNone(PartnerResponse.tenant_id)
        self.assertIsNotNone(PartnerResponse.object_id)
        self.assertIsNotNone(PartnerResponse.updated_time)
        self.assertIsNotNone(PartnerResponse.created_time)
        self.assertIsNotNone(PartnerResponse.state)
        self.assertIsNotNone(PartnerResponse.version)

    def setUp(self):
        super(MgmtPartnerTest, self).setUp()
        self.managementpartner_client = self.create_basic_client(ACEProvisioningManagementPartnerAPI)

    def test_managementpartner_get(self):
        self.partner_id="123456"
        managment_partner = self.managementpartner_client.partner.get(self.partner_id)
        self.assertIsNotNone(managment_partner)
        self._validate_partner(managment_partner)

    def test_managementpartner_create(self):
        self.partner_id="123456"
        managment_partner = self.managementpartner_client.partner.create(self.partner_id)
        self.assertIsNotNone(managment_partner)
        self._validate_partner(managment_partner)

    def test_managementpartner_update(self):
        self.partner_id="123457"
        managment_partner = self.managementpartner_client.partner.update(self.partner_id)
        self.assertIsNotNone(managment_partner)
        self._validate_partner(managment_partner)

    def test_managementpartner_delete(self):
        self.partner_id="123456"
        self.managementpartner_client.partner.delete(self.partner_id)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
