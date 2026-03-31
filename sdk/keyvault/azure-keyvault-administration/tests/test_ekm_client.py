# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.keyvault.administration import KeyVaultEkmClient, KeyVaultEkmConnection
from azure.keyvault.administration._internal.client_base import DEFAULT_VERSION

from devtools_testutils import recorded_by_proxy

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultEkmClientPreparer, get_decorator

only_latest = get_decorator(api_versions=[DEFAULT_VERSION])


class TestEkm(KeyVaultTestCase):
    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_create_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        ekm_connection = KeyVaultEkmConnection(
            host="my-ekm-host",
            server_ca_certificates=[b"my-fake-cert"],
            path_prefix="/ekm-path-prefix",
            server_subject_common_name="my-ekm-subject-common-name",
        )
        created_ekm_connection = client.create_ekm_connection(
            ekm_connection=ekm_connection
        )
        self.assertEqual(created_ekm_connection.host, ekm_connection.host)

    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_get_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        retrieved_ekm_connection = client.get_ekm_connection()
        assert retrieved_ekm_connection.host is not None

    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_get_ekm_certificate(self, client: KeyVaultEkmClient, **kwargs):
        ekm_certificate = client.get_ekm_certificate()
        assert ekm_certificate is not None

    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_check_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        connection_status = client.check_ekm_connection()
        assert connection_status is not None

    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_update_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        updated_ekm_connection = KeyVaultEkmConnection(
            host="my-updated-ekm-host",
            server_ca_certificates=[b"my-updated-fake-cert"],
            path_prefix="/updated-ekm-path-prefix",
            server_subject_common_name="my-updated-ekm-subject-common-name",
        )
        result = client.update_ekm_connection(ekm_connection=updated_ekm_connection)
        assert result.host == updated_ekm_connection.host

    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_delete_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        client.delete_ekm_connection()
