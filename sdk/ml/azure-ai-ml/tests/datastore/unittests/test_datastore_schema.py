import pytest
from test_utilities.utils import verify_entity_load_and_dump

import azure.ai.ml._schema._datastore as DatastoreSchemaDir
from azure.ai.ml import load_datastore
from azure.ai.ml._restclient.v2023_04_01_preview import models as models_preview
from azure.ai.ml._restclient.v2023_04_01_preview.models import AzureBlobDatastore as RestAzureBlobDatastore
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    AzureDataLakeGen1Datastore as RestAzureDataLakeGen1Datastore,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    AzureDataLakeGen2Datastore as RestAzureDataLakeGen2Datastore,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import AzureFileDatastore as RestAzureFileDatastore
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    NoneDatastoreCredentials,
    ServicePrincipalDatastoreCredentials,
)
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import DATASTORE_SCHEMA_TYPES
from azure.ai.ml.entities import (
    AzureBlobDatastore,
    AzureDataLakeGen1Datastore,
    AzureDataLakeGen2Datastore,
    AzureFileDatastore,
    OneLakeDatastore,
    Datastore,
)
from azure.ai.ml.entities._credentials import (
    AccountKeyConfiguration,
    NoneCredentialConfiguration,
    ServicePrincipalConfiguration,
)
from azure.ai.ml.entities._datastore._on_prem import HdfsDatastore
from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosKeytabCredentials, KerberosPasswordCredentials

kerberos_pw_yml = "hdfs_kerberos_pw.yml"
kerberos_keytab_yml = "hdfs_kerberos_keytab.yml"


def b64read(p):
    from base64 import b64encode

    with open(p, "rb") as f:
        return b64encode(f.read()).decode("utf-8")


@pytest.mark.unittest
@pytest.mark.skip(reason="Disable until preview release")
@pytest.mark.data_experiences_test
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

        def simple_datastore_validation(internal_ds):
            assert isinstance(internal_ds, HdfsDatastore)
            assert cfg["hdfs_server_certificate"] == internal_ds.hdfs_server_certificate
            assert cfg["name_node_address"] == internal_ds.name_node_address
            assert cfg["protocol"] == internal_ds.protocol
            assert isinstance(internal_ds.credentials, cred_type)
            assert cfg["credentials"]["kerberos_realm"] == internal_ds.credentials.kerberos_realm
            assert cfg["credentials"]["kerberos_kdc_address"] == internal_ds.credentials.kerberos_kdc_address
            assert cfg["credentials"]["kerberos_principal"] == internal_ds.credentials.kerberos_principal

        internal_ds = verify_entity_load_and_dump(load_datastore, simple_datastore_validation, test_path)[0]

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
        assert isinstance(internal_ds.credentials, AccountKeyConfiguration)
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
        assert isinstance(internal_ds.credentials, AccountKeyConfiguration)
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
        assert isinstance(internal_ds.credentials, NoneCredentialConfiguration)
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
        assert isinstance(internal_ds_from_rest.credentials, NoneCredentialConfiguration)
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
        assert isinstance(internal_credential, ServicePrincipalConfiguration)
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
        assert isinstance(internal_credential, ServicePrincipalConfiguration)
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

    def test_credential_less_one_lake_schema(self):
        test_path = "./tests/test_configs/datastore/credential_less_one_lake.yml"
        cfg = load_yaml(test_path)
        internal_ds = load_datastore(test_path)
        assert isinstance(internal_ds, OneLakeDatastore)
        assert cfg["artifact"] == internal_ds.artifact

        internal_credentials = internal_ds.credentials
        assert isinstance(internal_credentials, NoneCredentialConfiguration)
        assert cfg["one_lake_workspace_name"] == internal_ds.one_lake_workspace_name
        assert cfg["endpoint"] == internal_ds.endpoint

        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, models_preview.OneLakeDatastore)
        assert isinstance(ds_properties.credentials, NoneDatastoreCredentials)
        assert ds_properties.one_lake_workspace_name == cfg["one_lake_workspace_name"]
        assert ds_properties.endpoint == cfg["endpoint"]

        # test REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert internal_ds_from_rest == internal_ds

    def test_one_lake_schema_with_service_principal(self):
        test_path = "./tests/test_configs/datastore/one_lake.yml"
        self.validate_one_lake_schema_with_service_principal(
            test_yaml_file_path=test_path, auth_url_key="authority_url"
        )

    def test_one_lake_authority_url_backward_compatible_schema(self):
        test_path = "./tests/test_configs/datastore/one_lake_auth_url_back_compat.yml"
        self.validate_one_lake_schema_with_service_principal(
            test_yaml_file_path=test_path, auth_url_key="authority_uri"
        )

    def validate_one_lake_schema_with_service_principal(self, test_yaml_file_path, auth_url_key):
        cfg = load_yaml(test_yaml_file_path)
        internal_ds = load_datastore(test_yaml_file_path)
        assert isinstance(internal_ds, OneLakeDatastore)
        assert cfg["artifact"] == internal_ds.artifact

        cfg_credentials = cfg["credentials"]
        internal_credentials = internal_ds.credentials
        assert isinstance(internal_credentials, ServicePrincipalConfiguration)
        assert cfg_credentials["tenant_id"] == internal_credentials.tenant_id
        assert cfg_credentials["client_id"] == internal_credentials.client_id
        assert cfg_credentials["client_secret"] == internal_credentials.client_secret
        assert cfg_credentials["resource_url"] == internal_credentials.resource_url
        assert cfg_credentials[auth_url_key] == internal_credentials.authority_url

        assert cfg["one_lake_workspace_name"] == internal_ds.one_lake_workspace_name
        assert cfg["endpoint"] == internal_ds.endpoint

        # test REST translation
        datastore_resource = internal_ds._to_rest_object()
        datastore_resource.name = internal_ds.name
        ds_properties = datastore_resource.properties
        assert ds_properties
        assert isinstance(ds_properties, models_preview.OneLakeDatastore)
        assert isinstance(ds_properties.credentials, ServicePrincipalDatastoreCredentials)
        assert ds_properties.one_lake_workspace_name == cfg["one_lake_workspace_name"]
        assert ds_properties.endpoint == cfg["endpoint"]
        self.assert_rest_internal_service_principal_equal(ds_properties.credentials, internal_credentials)

        # test REST to internal translation
        internal_ds_from_rest = Datastore._from_rest_object(datastore_resource)
        assert internal_ds_from_rest == internal_ds

    def assert_rest_internal_service_principal_equal(
        self,
        rest_service_principal: ServicePrincipalDatastoreCredentials,
        internal_credential: ServicePrincipalConfiguration,
    ) -> None:
        assert rest_service_principal
        assert rest_service_principal.tenant_id
        assert rest_service_principal.tenant_id == internal_credential.tenant_id
        assert rest_service_principal.client_id
        assert rest_service_principal.client_id == internal_credential.client_id
        assert rest_service_principal.secrets
        assert rest_service_principal.secrets.client_secret == internal_credential.client_secret
        # authority_url gets set to https://login.microsoftonline.com by default
        assert rest_service_principal.authority_url
        assert rest_service_principal.authority_url == internal_credential.authority_url
        # resource_url doesn't get set to a default value so can be None
        assert rest_service_principal.resource_url == internal_credential.resource_url

    def test_all_datastore_schemas_included(self):
        """Test that all DatastoreSchemas are included in the DATASTORE_SCHEMA_TYPES constant"""
        import inspect

        clsmembers = [
            x[0]
            for x in inspect.getmembers(DatastoreSchemaDir, inspect.isclass)
            if x[0].endswith("Schema") and x[0].startswith("Azure")
        ]
        assert set(clsmembers) == set(DATASTORE_SCHEMA_TYPES)
