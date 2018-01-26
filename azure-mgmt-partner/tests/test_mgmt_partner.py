from azure.mgmt.partner import ACEProvisioningGSMAPI
from azure.mgmt.partner.models import PartnerResponse
from devtools_testutils import AzureMgmtTestCase
import unittest

class MgmtGsmTest(AzureMgmtTestCase):

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
        super(MgmtGsmTest, self).setUp()
        self.gsm_client = self.create_basic_client(ACEProvisioningGSMAPI)

    def test_partner_get(self):
        self.partner_id="123456"
        managment_partner = self.gsm_client.partner.get(self.partner_id)
        self.assertIsNotNone(managment_partner)
        self._validate_partner(managment_partner)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
