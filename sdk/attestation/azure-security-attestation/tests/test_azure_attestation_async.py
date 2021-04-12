import pytest
import asyncio
import functools
import os

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from devtools_testutils.azure_testcase import _is_autorest_v3
from devtools_testutils import AzureTestCase
from azure.security.attestation.aio import AttestationClient

class AsyncAzureAttestationTest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AsyncAzureAttestationTest, self).__init__(*args, **kwargs)
        self.location_name = os.environ.get('ATTESTATION_LOCATION_SHORT_NAME')

    def setUp(self):
        super(AsyncAzureAttestationTest, self).setUp()

    @AzureTestCase.await_prepared_test
    async def test_shared_getopenidmetadataasync(self):
        attest_client = self.shared_client()
        open_id_metadata = (await attest_client.get_openidmetadata())
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == self.shared_base_uri()+"/certs"
        assert open_id_metadata["issuer"] == self.shared_base_uri()

    def create_client(self, base_uri):
            """
            docstring
            """
            credential = self.get_credential(AttestationClient, is_async=True)
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                instance_url=base_uri)
            return attest_client

    def shared_client(self):
            """
            docstring
            """
            return self.create_client(self.shared_base_uri())

    def shared_base_uri(self):
        return 'https://shared'+self.location_name+'.'+self.location_name+'.attest.azure.net'
