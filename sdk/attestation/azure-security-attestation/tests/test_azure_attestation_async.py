import pytest
import asyncio
import functools
import os

from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from devtools_testutils.azure_testcase import _is_autorest_v3
from devtools_testutils import AzureTestCase
from azure.security.attestation.aio import AttestationClient

from preparers import AttestationPreparer


class AsyncAzureAttestationTest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AsyncAzureAttestationTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(AsyncAzureAttestationTest, self).setUp()

    @AttestationPreparer()
    @pytest.mark.live_test_only
    async def test_shared_getopenidmetadataasync(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        open_id_metadata = (await attest_client.get_openidmetadata())
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        if self.is_live:
            assert open_id_metadata["jwks_uri"] == self.shared_base_uri(attestation_location_short_name)+"/certs"
            assert open_id_metadata["issuer"] == self.shared_base_uri(attestation_location_short_name)

    def create_client(self, base_uri):
            """
            docstring
            """
            credential = self.get_credential(AttestationClient, is_async=True)
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                instance_url=base_uri)
            return attest_client

    def shared_client(self, location_name):
            """
            docstring
            """
            return self.create_client(self.shared_base_uri(location_name))

    def shared_base_uri(self, location_name: str):
        return 'https://shared' + location_name +'.'+ location_name + '.attest.azure.net'
