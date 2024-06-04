from typing import Callable, Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient, load_datastore
from azure.ai.ml.entities import AzureBlobDatastore, AzureFileDatastore
from azure.ai.ml.entities._credentials import NoneCredentialConfiguration
from azure.ai.ml.entities._datastore._on_prem import HdfsDatastore
from azure.ai.ml.entities._datastore.datastore import Datastore


def b64read(p):
    from base64 import b64encode

    with open(p, "rb") as f:
        return b64encode(f.read()).decode("utf-8")


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.data_experiences_test
class TestDatastore(AzureRecordedTestCase):
    @pytest.mark.skip(reason="Disable until preview release")
    def test_hdfs_pw(
        self,
        client: MLClient,
        hdfs_pw_file: str,
        randstr: Callable[[str], str],
    ) -> None:
        random_name = randstr("random_name")
        params_override = [
            {"name": random_name},
        ]
        internal_blob_ds = load_datastore(hdfs_pw_file, params_override=params_override)
        created_datastore = datastore_create_get_list(client, internal_blob_ds, random_name)
        assert isinstance(created_datastore, HdfsDatastore)
        assert created_datastore.credentials.kerberos_password == internal_blob_ds.credentials.kerberos_password

        # must reset for path/value fields
        created_datastore = load_datastore(hdfs_pw_file, params_override=params_override)
        created_datastore.credentials.kerberos_password = "placeholderPwd"
        client.datastores.create_or_update(created_datastore)
        updated_datastore = client.datastores.get(created_datastore.name, include_secrets=True)
        assert updated_datastore.credentials.kerberos_password == "placeholderPwd"

        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    @pytest.mark.skip(reason="Disable until preview release")
    def test_hdfs_keytab(
        self,
        client: MLClient,
        hdfs_keytab_file: str,
        randstr: Callable[[str], str],
    ) -> None:
        random_name = randstr("random_name")
        params_override = [
            {"name": random_name},
        ]
        internal_blob_ds = load_datastore(hdfs_keytab_file, params_override=params_override)
        created_datastore = datastore_create_get_list(client, internal_blob_ds, random_name)
        assert isinstance(created_datastore, HdfsDatastore)
        first_created_keytab_value = created_datastore.credentials.kerberos_keytab
        assert created_datastore.credentials.kerberos_keytab == b64read(internal_blob_ds.credentials.kerberos_keytab)

        # must reset for path/value fields
        created_datastore = load_datastore(hdfs_keytab_file, params_override=params_override)
        created_datastore.credentials.kerberos_keytab = created_datastore.credentials.kerberos_keytab.replace(
            ".yml", "2.yml"
        )
        client.datastores.create_or_update(created_datastore)
        updated_datastore = client.datastores.get(created_datastore.name, include_secrets=True)
        assert updated_datastore.credentials.kerberos_keytab == b64read(created_datastore.credentials.kerberos_keytab)
        assert updated_datastore.credentials.kerberos_keytab != first_created_keytab_value

        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_blob_store(
        self,
        client: MLClient,
        blob_store_file: str,
        storage_account_name: str,
        account_keys: Tuple[str, str],
        randstr: Callable[[str], str],
    ) -> None:
        primary_account_key, secondary_account_key = account_keys
        random_name = randstr("random_name")
        params_override = [
            {"credentials.account_key": primary_account_key},
            {"name": random_name},
            {"account_name": storage_account_name},
        ]
        internal_blob_ds = load_datastore(blob_store_file, params_override=params_override)
        created_datastore = datastore_create_get_list(client, internal_blob_ds, random_name)
        assert isinstance(created_datastore, AzureBlobDatastore)
        assert created_datastore.container_name == internal_blob_ds.container_name
        assert created_datastore.account_name == internal_blob_ds.account_name
        assert created_datastore.credentials.account_key == primary_account_key
        datastore_update_check_credential(client, created_datastore, secondary_account_key)
        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_blob_store_credential_less(
        self,
        client: MLClient,
        blob_store_credential_less_file: str,
        storage_account_name: str,
        randstr: Callable[[str], str],
    ) -> None:
        random_name = randstr("random_name")
        params_override = [
            {"name": random_name},
            {"account_name": storage_account_name},
        ]
        internal_blob_ds = load_datastore(blob_store_credential_less_file, params_override=params_override)
        created_datastore = datastore_create_get_list(client, internal_blob_ds, random_name)
        assert isinstance(created_datastore, AzureBlobDatastore)
        assert created_datastore.container_name == internal_blob_ds.container_name
        assert created_datastore.account_name == internal_blob_ds.account_name
        assert isinstance(created_datastore.credentials, NoneCredentialConfiguration)
        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_file_store(
        self,
        client: MLClient,
        file_store_file: str,
        storage_account_name: str,
        account_keys: str,
        randstr: Callable[[str], str],
    ) -> None:
        primary_account_key, secondary_account_key = account_keys
        random_name = randstr("random_name")
        params_override = [
            {"credentials.account_key": primary_account_key},
            {"name": random_name},
            {"account_name": storage_account_name},
        ]
        internal_file_ds = load_datastore(file_store_file, params_override=params_override)
        created_datastore = datastore_create_get_list(client, internal_file_ds, random_name)
        assert isinstance(created_datastore, AzureFileDatastore)
        assert created_datastore.file_share_name == internal_file_ds.file_share_name
        assert created_datastore.account_name == internal_file_ds.account_name
        assert created_datastore.credentials.account_key == primary_account_key
        datastore_update_check_credential(client, created_datastore, secondary_account_key)
        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    @pytest.mark.skip(
        reason="Will reenable once we have a service principal: https://msdata.visualstudio.com/Vienna/_workitems/edit/1071904/"
    )
    def test_adls_gen_1_store(
        self,
        client: MLClient,
        adls_gen1_file: str,
        randstr: Callable[[str], str],
    ) -> None:
        random_name = randstr("random_name")
        internal_adls_gen1 = load_datastore(adls_gen1_file, client._operation_scope)
        created_datastore = datastore_create_get_list(client, adls_gen1_file, random_name)
        assert created_datastore.store_name == internal_adls_gen1.store_name
        assert created_datastore.credentials.tenant_id == internal_adls_gen1.credentials.tenant_id
        assert created_datastore.credentials.client_id == internal_adls_gen1.credentials.client_id
        assert created_datastore.credentials.client_secret == internal_adls_gen1.credentials.client_secret
        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    @pytest.mark.skip(
        reason="Will reenable once service been fixed: Bug 1423343: [DPv2 - Data] Credential-less datastore creation fails for ADLS Gen1 datastores"
    )
    def test_credential_less_adls_gen_1_store(
        self,
        client: MLClient,
        adls_gen1_credential_less_file: str,
        randstr: Callable[[str], str],
    ) -> None:
        random_name = randstr("random_name")
        params_override = [
            {"name": random_name},
        ]
        internal_adls_gen1 = load_datastore(adls_gen1_credential_less_file, params_override=params_override)
        created_datastore = datastore_create_get_list(client, internal_adls_gen1, random_name)
        assert created_datastore.store_name == internal_adls_gen1.store_name
        assert isinstance(created_datastore.credentials, NoneCredentialConfiguration)
        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    @pytest.mark.skip(
        reason="Will reenable once we have a service principal: https://msdata.visualstudio.com/Vienna/_workitems/edit/1071904/"
    )
    def test_adls_gen2_store(
        self,
        client: MLClient,
        adls_gen2_file: str,
        randstr: Callable[[str], str],
    ) -> None:
        random_name = randstr("random_name")
        internal_adls_gen2 = load_datastore(adls_gen2_file, client._operation_scope)
        created_datastore = datastore_create_get_list(client, adls_gen2_file, random_name)
        assert created_datastore.account_name == internal_adls_gen2.account_name
        assert created_datastore.credentials.tenant_id == internal_adls_gen2.credentials.tenant_id
        assert created_datastore.credentials.client_id == internal_adls_gen2.credentials.client_id
        assert created_datastore.credentials.client_secret == internal_adls_gen2.credentials.client_secret
        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_credential_less_adls_gen2_store(
        self,
        client: MLClient,
        adls_gen2_credential_less_file: str,
        randstr: Callable[[str], str],
    ) -> None:
        random_name = randstr("random_name")
        params_override = [
            {"name": random_name},
        ]
        internal_adls_gen2 = load_datastore(adls_gen2_credential_less_file, params_override=params_override)
        created_datastore = datastore_create_get_list(client, internal_adls_gen2, random_name)
        assert created_datastore.account_name == internal_adls_gen2.account_name
        assert isinstance(created_datastore.credentials, NoneCredentialConfiguration)
        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)


def datastore_create_get_list(client: MLClient, datastore: Datastore, random_name: str) -> Datastore:
    client.datastores.create_or_update(datastore)
    datastore = client.datastores.get(random_name, include_secrets=True)
    assert datastore.name == random_name
    ds_list = client.datastores.list()
    assert any(ds.name == datastore.name for ds in ds_list)
    return datastore


def datastore_update_check_credential(
    client: MLClient, created_datastore: Datastore, secondary_account_key: str
) -> None:
    # Update datastore with a new credential
    created_datastore.credentials.account_key = secondary_account_key
    client.datastores.create_or_update(created_datastore)
    updated_datastore = client.datastores.get(created_datastore.name, include_secrets=True)
    if is_live():
        assert updated_datastore.credentials.account_key == secondary_account_key
