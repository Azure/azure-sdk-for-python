import pytest

from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities._datastore.credentials import (
    AccountKeyCredentials,
    ServicePrincipalCredentials,
    NoneCredentials,
)
from azure.ai.ml.entities._datastore._on_prem_credentials import (
    KerberosKeytabCredentials,
    KerberosPasswordCredentials,
)
from azure.ai.ml._restclient.v2022_05_01.models import (
    AzureFileDatastore as RestAzureFileDatastore,
    AzureBlobDatastore as RestAzureBlobDatastore,
    AzureDataLakeGen1Datastore as RestAzureDataLakeGen1Datastore,
    AzureDataLakeGen2Datastore as RestAzureDataLakeGen2Datastore,
    ServicePrincipalDatastoreCredentials,
    NoneDatastoreCredentials,
)
from azure.ai.ml._restclient.v2022_02_01_preview import models as models_preview
from azure.ai.ml.entities import (
    AzureFileDatastore,
    AzureBlobDatastore,
    AzureDataLakeGen1Datastore,
    AzureDataLakeGen2Datastore,
    Datastore,
)
from azure.ai.ml.entities._datastore._on_prem import HdfsDatastore
from azure.ai.ml import load_datastore

kerberos_pw_yml = "hdfs_kerberos_pw.yml"
kerberos_keytab_yml = "hdfs_kerberos_keytab.yml"


def b64read(p):
    from base64 import b64encode

    with open(p, "rb") as f:
        return b64encode(f.read()).decode("utf-8")


@pytest.mark.unittest
@pytest.mark.skip(reason="Disable until preview release")
class TestHdfsDatastore:
    @pytest.mark.parametrize(
        "path, cred_type, is_key_tab",
        [
            (kerberos_pw_yml, KerberosPasswordCredentials, False),
            (kerberos_keytab_yml, KerberosKeytabCredentials, True),
        ],
    )
    def test_kerberos_schema(self, path, cred_type, is_key_tab):
        test_path = f"./tests/test_configs/datastore/{path}"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert isinstance(internal_ds, HdfsDatastore)
        assert cfg["hdfs_server_certificate"] == internal_ds.hdfs_server_certificate
        assert cfg["name_node_address"] == internal_ds.name_node_address
        assert cfg["protocol"] == internal_ds.protocol
        assert isinstance(internal_ds.credentials, cred_type)
        assert cfg["credentials"]["kerberos_realm"] == internal_ds.credentials.kerberos_realm
        assert cfg["credentials"]["kerberos_kdc_address"] == internal_ds.credentials.kerberos_kdc_address
        assert cfg["credentials"]["kerberos_principal"] == internal_ds.credentials.kerberos_principal

        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, models_preview.HdfsDatastore)
        assert ds_properties.hdfs_server_certificate == b64read(internal_ds.hdfs_server_certificate)
        assert ds_properties.name_node_address == internal_ds.name_node_address
        assert ds_properties.protocol == internal_ds.protocol
        # test the REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert isinstance(internal_ds_from_rest.credentials, cred_type)
        # workaround for base 64 encoded values
        internal_ds.hdfs_server_certificate = b64read(internal_ds.hdfs_server_certificate)
        if is_key_tab and internal_ds.credentials.kerberos_keytab:
            internal_ds.credentials.kerberos_keytab = b64read(internal_ds.credentials.kerberos_keytab)
        assert internal_ds_from_rest == internal_ds

    def test_kerberos_password_schema(self):
        test_path = f"./tests/test_configs/datastore/{kerberos_pw_yml}"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert cfg["credentials"]["kerberos_password"] == internal_ds.credentials.kerberos_password

    def test_kerberos_keytab_schema(self):
        test_path = f"./tests/test_configs/datastore/{kerberos_keytab_yml}"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert cfg["credentials"]["kerberos_keytab"] == internal_ds.credentials.kerberos_keytab

    def test_minimum_schema(self):
        test_path = "./tests/test_configs/datastore/hdfs_kerberos_minimal.yml"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert isinstance(internal_ds, HdfsDatastore)
        assert internal_ds.hdfs_server_certificate is None
        assert "hdfs_server_certificate" not in cfg
        assert cfg["name_node_address"] == internal_ds.name_node_address
        assert internal_ds.protocol == "http"
        assert "protocol" not in cfg
        assert isinstance(internal_ds.credentials, KerberosPasswordCredentials)
        assert cfg["credentials"]["kerberos_realm"] == internal_ds.credentials.kerberos_realm
        assert cfg["credentials"]["kerberos_kdc_address"] == internal_ds.credentials.kerberos_kdc_address
        assert cfg["credentials"]["kerberos_principal"] == internal_ds.credentials.kerberos_principal

        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, models_preview.HdfsDatastore)
        assert ds_properties.hdfs_server_certificate == internal_ds.hdfs_server_certificate
        assert ds_properties.name_node_address == internal_ds.name_node_address
        assert ds_properties.protocol == internal_ds.protocol
        # test the REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert internal_ds_from_rest.protocol == "http"
        assert isinstance(internal_ds_from_rest.credentials, KerberosPasswordCredentials)
        assert internal_ds_from_rest == internal_ds


@pytest.mark.unittest
class TestDatastore:
    def test_file_share_schema(self):
        test_path = "./tests/test_configs/datastore/file_store.yml"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert isinstance(internal_ds, AzureFileDatastore)
        assert cfg["account_name"] == internal_ds.account_name
        assert isinstance(internal_ds.credentials, AccountKeyCredentials)
        assert cfg["credentials"]["account_key"] == internal_ds.credentials.account_key
        assert cfg["file_share_name"] == internal_ds.file_share_name
        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, RestAzureFileDatastore)
        assert ds_properties.account_name == internal_ds.account_name
        assert ds_properties.file_share_name == internal_ds.file_share_name
        assert ds_properties.credentials.secrets.key
        assert ds_properties.credentials.secrets.key == internal_ds.credentials.account_key
        # test the REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert internal_ds_from_rest == internal_ds

    def test_blob_store_schema(self):
        test_path = "./tests/test_configs/datastore/blob_store.yml"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert isinstance(internal_ds, AzureBlobDatastore)
        assert cfg["account_name"] == internal_ds.account_name
        assert isinstance(internal_ds.credentials, AccountKeyCredentials)
        assert cfg["credentials"]["account_key"] == internal_ds.credentials.account_key
        assert cfg["container_name"] == internal_ds.container_name
        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, RestAzureBlobDatastore)
        assert ds_properties.account_name == internal_ds.account_name
        assert ds_properties.container_name == internal_ds.container_name
        assert ds_properties.credentials.secrets.key
        assert ds_properties.credentials.secrets.key == internal_ds.credentials.account_key
        # test the REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert internal_ds_from_rest == internal_ds

    def test_credential_less_blob_store_schema(self):
        test_path = "./tests/test_configs/datastore/credential_less_blob_store.yml"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert isinstance(internal_ds, AzureBlobDatastore)
        assert cfg["account_name"] == internal_ds.account_name
        assert isinstance(internal_ds.credentials, NoneCredentials)
        assert cfg["container_name"] == internal_ds.container_name
        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, RestAzureBlobDatastore)
        assert ds_properties.account_name == internal_ds.account_name
        assert ds_properties.container_name == internal_ds.container_name
        assert isinstance(ds_properties.credentials, NoneDatastoreCredentials)
        # test the REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert isinstance(internal_ds_from_rest.credentials, NoneCredentials)
        assert internal_ds_from_rest.credentials == internal_ds.credentials
        assert internal_ds_from_rest == internal_ds

    def test_adls_gen1_schema(self):
        test_path = "./tests/test_configs/datastore/adls_gen1.yml"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert isinstance(internal_ds, AzureDataLakeGen1Datastore)
        assert cfg["store_name"] == internal_ds.store_name
        cfg_credential = cfg["credentials"]
        internal_credential = internal_ds.credentials
        assert isinstance(internal_credential, ServicePrincipalCredentials)
        assert cfg_credential["tenant_id"] == internal_credential.tenant_id
        assert cfg_credential["client_id"] == internal_credential.client_id
        assert cfg_credential["client_secret"] == internal_credential.client_secret
        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, RestAzureDataLakeGen1Datastore)
        assert ds_properties.store_name == internal_ds.store_name
        self.assert_rest_internal_service_principal_equal(ds_properties.credentials, internal_credential)
        # test the REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert internal_ds_from_rest == internal_ds

    def test_adls_gen2_schema(self):
        test_path = "./tests/test_configs/datastore/adls_gen2.yml"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert isinstance(internal_ds, AzureDataLakeGen2Datastore)
        assert cfg["account_name"] == internal_ds.account_name
        cfg_credential = cfg["credentials"]
        internal_credential = internal_ds.credentials
        assert isinstance(internal_credential, ServicePrincipalCredentials)
        assert cfg_credential["tenant_id"] == internal_credential.tenant_id
        assert cfg_credential["client_id"] == internal_credential.client_id
        assert cfg_credential["client_secret"] == internal_credential.client_secret
        assert cfg["filesystem"] == internal_ds.filesystem
        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, RestAzureDataLakeGen2Datastore)
        assert ds_properties.account_name == cfg["account_name"]
        assert ds_properties.filesystem == cfg["filesystem"]
        self.assert_rest_internal_service_principal_equal(ds_properties.credentials, internal_credential)
        # test the REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert internal_ds_from_rest == internal_ds

    def assert_rest_internal_service_principal_equal(
        self,
        rest_service_principal: ServicePrincipalDatastoreCredentials,
        internal_credential: ServicePrincipalCredentials,
    ) -> None:
        assert rest_service_principal
        assert rest_service_principal.tenant_id
        assert rest_service_principal.tenant_id == internal_credential.tenant_id
        assert rest_service_principal.client_id
        assert rest_service_principal.client_id == internal_credential.client_id
        assert rest_service_principal.secrets
        assert rest_service_principal.secrets.client_secret == internal_credential.client_secret
