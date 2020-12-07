import unittest
from devtools_testutils import AzureTestCase, ResourceGroupPreparer, PowerShellPreparer
import functools
import json
import cryptography
import base64

from azure.security.attestation.v2020_10_01 import AttestationClient
from  maa_test_common import AttestationPreparer, shared_uks_base_uri

class AttestationTestMetadata(AzureTestCase):

  def setUp(self):
        super(AttestationTestMetadata, self).setUp()
        print('starting up')

  @AttestationPreparer()
  def test_shared_getopenidmetadata(self):
    credential = self.get_credential(AttestationClient)
    attest_client = self.create_client_from_credential(AttestationClient, credential=credential, tenant_base_url=shared_uks_base_uri)
    open_id_metadata = attest_client.metadata_configuration.get()
    print ('{}'.format(open_id_metadata))
    assert open_id_metadata["response_types_supported"] is not None
    assert open_id_metadata["jwks_uri"] == shared_uks_base_uri+"/certs"
    assert open_id_metadata["issuer"] == shared_uks_base_uri

  def test_shared_getsigningcertificates(self):
    credential = self.get_credential(AttestationClient)
    attest_client = self.create_client_from_credential(AttestationClient, credential=credential, tenant_base_url=shared_uks_base_uri)
    signing_certificates = attest_client.signing_certificates.get()
    print ('{}'.format(signing_certificates))
    assert signing_certificates["keys"] is not None
    keys = signing_certificates["keys"]
    assert len(keys) != 0
    for key in keys:
      assert key["x5c"] is not None
      x5cs = key["x5c"]
      assert len(x5cs) >= 1
      print('Found key with x5c, length = {}', len(x5cs))
      for x5c in x5cs:
        der_cert = base64.b64decode(x5c)
        cert = cryptography.x509.load_der_x509_certificate(der_cert)
        print(f'Cert  iss: {cert.issuer}; subject: {cert.subject}')



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
