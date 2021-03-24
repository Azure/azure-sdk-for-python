# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import json
import os
import tempfile
import unittest
import pytest
try:
    from unittest import mock
except ImportError:
    import mock
from io import open

from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD
# https://github.com/Azure/azure-cli/blob/4e1ff0ec626ea46d74793ad92a1b5eddc2b6e45b/src/azure-cli-core/azure/cli/core/cloud.py#L310
AZURE_PUBLIC_CLOUD.endpoints.app_insights_resource_id='https://api.applicationinsights.io'

from azure.common.client_factory import *

class TestCommon(unittest.TestCase):

    @mock.patch('azure.common.client_factory.get_cli_active_cloud')
    @mock.patch('azure.common.client_factory.get_azure_cli_credentials')
    def test_get_client_from_cli_profile(self, get_azure_cli_credentials, get_cli_active_cloud):

        class FakeClient(object):
            def __init__(self, credentials, subscription_id, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if subscription_id is None:
                    raise ValueError("Parameter 'subscription_id' must not be None.")
                if not isinstance(subscription_id, str):
                    raise TypeError("Parameter 'subscription_id' must be str.")
                if not base_url:
                    base_url = 'should not be used'

                self.credentials = credentials
                self.subscription_id = subscription_id
                self.base_url = base_url

        class FakeSubscriptionClient(object):
            def __init__(self, credentials, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if not base_url:
                    base_url = 'should not be used'

                self.credentials = credentials
                self.base_url = base_url

        class GraphRbacManagementClient(object):
            def __init__(self, credentials, tenant_id, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if tenant_id is None:
                    raise ValueError("Parameter 'tenant_id' must not be None.")
                if not base_url:
                    base_url = 'should not be used'

                self.credentials = credentials
                self.tenant_id = tenant_id
                self.base_url = base_url

        class ApplicationInsightsDataClient(object):
            def __init__(self, credentials, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if not base_url:
                    base_url = 'should not be used'

                self.credentials = credentials
                self.base_url = base_url

        class KeyVaultClient(object):
            def __init__(self, credentials):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")

                self.credentials = credentials

        get_cli_active_cloud.return_value = AZURE_PUBLIC_CLOUD
        get_azure_cli_credentials.return_value = 'credentials', 'subscription_id', 'tenant_id'

        client = get_client_from_cli_profile(FakeClient)
        get_azure_cli_credentials.assert_called_with(resource=None, with_tenant=True)
        assert client.credentials == 'credentials'
        assert client.subscription_id == 'subscription_id'
        assert client.base_url == "https://management.azure.com/"

        client = get_client_from_cli_profile(FakeSubscriptionClient)
        get_azure_cli_credentials.assert_called_with(resource=None, with_tenant=True)
        assert client.credentials == 'credentials'
        assert client.base_url == "https://management.azure.com/"

        client = get_client_from_cli_profile(GraphRbacManagementClient)
        get_azure_cli_credentials.assert_called_with(resource="https://graph.windows.net/", with_tenant=True)
        assert client.credentials == 'credentials'
        assert client.tenant_id == 'tenant_id'
        assert client.base_url == "https://graph.windows.net/"

        client = get_client_from_cli_profile(ApplicationInsightsDataClient)
        get_azure_cli_credentials.assert_called_with(resource="https://api.applicationinsights.io", with_tenant=True)
        assert client.credentials == 'credentials'
        assert client.base_url == "https://api.applicationinsights.io/v1"

        client = get_client_from_cli_profile(KeyVaultClient)
        get_azure_cli_credentials.assert_called_with(resource="https://vault.azure.net", with_tenant=True)
        assert client.credentials == 'credentials'


    @mock.patch('azure.common.client_factory.get_cli_active_cloud')
    @mock.patch('azure.common.client_factory.get_azure_cli_credentials')
    def test_get_client_from_cli_profile_core(self, get_azure_cli_credentials, get_cli_active_cloud):

        class KeyVaultClientBase(object):
            def __init__(self, vault_url, credential):
                if not credential:
                    raise ValueError(
                        "credential should be an object supporting the TokenCredential protocol, "
                        "such as a credential from azure-identity"
                    )
                if not vault_url:
                    raise ValueError("vault_url must be the URL of an Azure Key Vault")
                self.credential = credential
                self.vault_url = vault_url

        class NewKeyVaultClient(KeyVaultClientBase):
            pass

        class StorageAccountHostsMixin(object):
            def __init__(
                    self, account_url,  # type: str
                    credential=None,  # type: Optional[Any]
                    **kwargs  # type: Any
                ):
                try:
                    if not account_url.lower().startswith('http'):
                        account_url = "https://" + account_url
                except AttributeError:
                    raise ValueError("Account URL must be a string.")

                self.credential = credential
                self.account_url = account_url

        class BlobServiceClient(StorageAccountHostsMixin):
            pass

        get_cli_active_cloud.return_value = AZURE_PUBLIC_CLOUD
        get_azure_cli_credentials.return_value = 'credential', 'subscription_id', 'tenant_id'

        client = get_client_from_cli_profile(NewKeyVaultClient, vault_url="foo")
        assert client.credential == 'credential'
        assert client.vault_url == "foo"

        client = get_client_from_cli_profile(BlobServiceClient, account_url="foo")
        assert client.credential == 'credential'
        assert client.account_url == "https://foo"

        client = get_client_from_cli_profile(BlobServiceClient, account_url="foo", credential=None)
        assert client.credential == None
        assert client.account_url == "https://foo"


    def test_get_client_from_auth_file(self):

        configuration = {
            "clientId": "a2ab11af-01aa-4759-8345-7803287dbd39",
            "clientSecret": "password",
            "subscriptionId": "15dbcfa8-4b93-4c9a-881c-6189d39f04d4",
            "tenantId": "c81da1d8-65ca-11e7-b1d1-ecb1d756380e",
            "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
            "resourceManagerEndpointUrl": "https://management.azure.com/",
            "activeDirectoryGraphResourceId": "https://graph.windows.net/",
            "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
            "galleryEndpointUrl": "https://gallery.azure.com/",
            "managementEndpointUrl": "https://management.core.windows.net/"
        }

        class FakeClient(object):
            def __init__(self, credentials, subscription_id, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if subscription_id is None:
                    raise ValueError("Parameter 'subscription_id' must not be None.")
                if not isinstance(subscription_id, str):
                    raise TypeError("Parameter 'subscription_id' must be str.")
                if not base_url:
                    base_url = 'should not be used'

                self.credentials = credentials
                self.subscription_id = subscription_id
                self.base_url = base_url

        class FakeSubscriptionClient(object):
            def __init__(self, credentials, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if not base_url:
                    base_url = 'should not be used'

                self.credentials = credentials
                self.base_url = base_url

        class GraphRbacManagementClient(object):
            def __init__(self, credentials, tenant_id, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if tenant_id is None:
                    raise ValueError("Parameter 'tenant_id' must not be None.")
                if not base_url:
                    base_url = 'should not be used'

                self.credentials = credentials
                self.tenant_id = tenant_id
                self.base_url = base_url

        class KeyVaultClient(object):
            def __init__(self, credentials):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")

                self.credentials = credentials

        class KeyVaultClientTrack2(object):
            def __init__(self, credential):
                if credential is None:
                    raise ValueError("Parameter 'credentials' must not be None.")

                self.credential = credential

        for encoding in ['utf-8', 'utf-8-sig', 'ascii']:

            temp_auth_file = tempfile.NamedTemporaryFile(delete=False)
            temp_auth_file.write(json.dumps(configuration).encode(encoding))
            temp_auth_file.close()

            client = get_client_from_auth_file(FakeClient, temp_auth_file.name)
            self.assertEqual('15dbcfa8-4b93-4c9a-881c-6189d39f04d4', client.subscription_id)
            self.assertEqual('https://management.azure.com/', client.base_url)
            self.assertTupleEqual(client.credentials._args, (
                'https://management.azure.com/',
                'a2ab11af-01aa-4759-8345-7803287dbd39',
                'password'
            ))

            client = get_client_from_auth_file(FakeClient, temp_auth_file.name, subscription_id='fakesubid')
            self.assertEqual('fakesubid', client.subscription_id)
            self.assertEqual('https://management.azure.com/', client.base_url)
            self.assertTupleEqual(client.credentials._args, (
                'https://management.azure.com/',
                'a2ab11af-01aa-4759-8345-7803287dbd39',
                'password'
            ))

            credentials_instance = "Fake credentials class as a string"
            client = get_client_from_auth_file(FakeClient, temp_auth_file.name, credentials=credentials_instance)
            self.assertEqual('15dbcfa8-4b93-4c9a-881c-6189d39f04d4', client.subscription_id)
            self.assertEqual('https://management.azure.com/', client.base_url)
            self.assertEqual(credentials_instance, client.credentials)

            client = get_client_from_auth_file(FakeSubscriptionClient, temp_auth_file.name)
            self.assertEqual('https://management.azure.com/', client.base_url)
            self.assertTupleEqual(client.credentials._args, (
                'https://management.azure.com/',
                'a2ab11af-01aa-4759-8345-7803287dbd39',
                'password'
            ))

            client = get_client_from_auth_file(GraphRbacManagementClient, temp_auth_file.name)
            assert client.base_url == 'https://graph.windows.net/'
            assert client.tenant_id == "c81da1d8-65ca-11e7-b1d1-ecb1d756380e"
            assert client.credentials._args == (
                "https://graph.windows.net/",
                'a2ab11af-01aa-4759-8345-7803287dbd39',
                'password'
            )

            client = get_client_from_auth_file(KeyVaultClient, temp_auth_file.name)
            assert client.credentials._args == (
                "https://vault.azure.net",
                'a2ab11af-01aa-4759-8345-7803287dbd39',
                'password'
            )

            with pytest.raises(ValueError) as excinfo:
                get_client_from_auth_file(KeyVaultClientTrack2, temp_auth_file.name)
            assert "https://aka.ms/azsdk/python/azidmigration" in str(excinfo.value)

            os.unlink(temp_auth_file.name)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
