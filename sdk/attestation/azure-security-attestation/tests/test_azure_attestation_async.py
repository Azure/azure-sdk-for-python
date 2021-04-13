import pytest
import asyncio
import functools
import os

from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from devtools_testutils.azure_testcase import _is_autorest_v3
from devtools_testutils import AzureTestCase
from azure.security.attestation.aio import AttestationClient

AttestationPreparer = functools.partial(
            PowerShellPreparer, "attestation",
#            attestation_azure_authority_host='xxx',
#            attestation_resource_group='yyyy',
#            attestation_subscription_id='xxx',
#            attestation_environment='AzureCloud',
            attestation_policy_signing_key0='keyvalue',
            attestation_policy_signing_key1='keyvalue',
            attestation_policy_signing_key2='keyvalue',
            attestation_policy_signing_certificate0='more junk',
            attestation_policy_signing_certificate1='more junk',
            attestation_policy_signing_certificate2='more junk',
            attestation_serialized_policy_signing_key0="junk",
            attestation_serialized_policy_signing_key1="junk",
            attestation_serialized_policy_signing_key2="junk",
            attestation_serialized_isolated_signing_key='yyyy',
            attestation_isolated_signing_key='xxxx',
            attestation_isolated_signing_certificate='xxxx',
            attestation_service_management_url='https://management.core.windows.net/',
            attestation_location_short_name='xxxx',
            attestation_client_id='xxxx',
            attestation_client_secret='secret',
            attestation_tenant_id='tenant',
            attestation_isolated_url='https://fakeresource.wus.attest.azure.net',
            attestation_aad_url='https://fakeresource.wus.attest.azure.net',
#            attestation_resource_manager_url='https://resourcemanager/zzz'
        )


class AsyncAzureAttestationTest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AsyncAzureAttestationTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(AsyncAzureAttestationTest, self).setUp()

    @AttestationPreparer()
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
