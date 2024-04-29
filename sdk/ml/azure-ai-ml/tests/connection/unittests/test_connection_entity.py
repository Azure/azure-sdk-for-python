from hmac import new
from pathlib import Path
from marshmallow.exceptions import ValidationError
import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_connection
from azure.ai.ml._restclient.v2024_04_01_preview.models import ConnectionAuthType, ConnectionCategory
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import Connection, AzureOpenAIConnection
from azure.ai.ml.constants._common import ConnectionTypes, CognitiveServiceKinds

from azure.ai.ml.entities._credentials import (
    AccessKeyConfiguration,
    ApiKeyConfiguration,
    ManagedIdentityConfiguration,
    NoneCredentialConfiguration,
    PatTokenConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
    UsernamePasswordConfiguration,
    _BaseIdentityConfiguration,
)

from azure.ai.ml.entities import (
    AzureBlobStoreConnection,
    MicrosoftOneLakeConnection,
    AzureOpenAIConnection,
    AzureAIServiceConnection,
    AzureAISearchConnection,
    AzureContentSafetyConnection,
    AzureSpeechServicesConnection,
    APIKeyConnection,
    OpenAIConnection,
    SerpConnection,
    ServerlessConnection,
)


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestWorkspaceConnectionEntity:
    def check_rest_conversion_stable(self, conn: Connection):
        """Helper function which converts an inputted connection to its rest
        equivalent and back again, then checks that they're still the same.

        :param conn: The connection to check
        :type conn: ~azure.ai.ml.entities.Connection
        """

        rest_conn = conn._to_rest_object()
        new_conn = Connection._from_rest_object(rest_obj=rest_conn)
        # Connections should be identical besides their name (which is not set by RestClient objects without API calls)
        # Check them individually to simplify debugging.
        assert new_conn is not None
        assert type(conn) == type(new_conn)
        assert conn.type == new_conn.type
        assert conn.target == new_conn.target
        assert conn.tags == new_conn.tags  # This helpfully compares hidden metadata for subclasses.
        assert conn.credentials == new_conn.credentials

    def test_workspace_connection_constructor(self):
        ws_connection = Connection(
            target="dummy_target",
            type=camel_to_snake(ConnectionCategory.PYTHON_FEED),
            credentials=PatTokenConfiguration(pat="dummy_pat"),
            name="dummy_connection",
            tags=None,
        )

        assert ws_connection.name == "dummy_connection"
        assert ws_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
        assert ws_connection.credentials.pat == "dummy_pat"
        assert ws_connection.target == "dummy_target"
        assert ws_connection.tags == {}

    # New connection tests - these connections have had their lists of acceptable credentials validated in 2024

    def test_workspace_connection_entity_load_and_dump(self):
        def simple_workspace_connection_validation(ws_connection):
            assert ws_connection.name == "test_ws_conn_git_pat"
            assert ws_connection.target == "https://test-git-feed.com"
            assert ws_connection.type == camel_to_snake(ConnectionCategory.GIT)
            assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
            assert ws_connection.credentials.pat == "dummy_pat"
            assert ws_connection.tags == {}

        verify_entity_load_and_dump(
            load_connection,
            simple_workspace_connection_validation,
            "./tests/test_configs/connection/git_pat.yaml",
        )

    def test_blob_storage(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/blob_store_acc_key.yaml")
        assert type(ws_connection) == AzureBlobStoreConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_BLOB)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.ACCOUNT_KEY)
        assert ws_connection.credentials.account_key == "9876"
        assert ws_connection.name == "test_ws_conn_blob_store1"
        assert ws_connection.url == "my_endpoint"
        assert ws_connection.tags["four"] == "five"
        assert ws_connection.container_name == "some_container"
        assert ws_connection.account_name == "some_account"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/blob_store_sas.yaml")
        assert type(ws_connection) == AzureBlobStoreConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_BLOB)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.SAS)
        assert ws_connection.credentials.sas_token == "some_pat"
        assert ws_connection.name == "test_ws_conn_blob_store2"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/blob_store_entra.yaml")
        assert type(ws_connection) == AzureBlobStoreConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_BLOB)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.AAD)
        assert ws_connection.name == "test_ws_conn_blob_store3"
        self.check_rest_conversion_stable(ws_connection)

    def test_alds_gen2(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/alds_gen2_sp.yaml")
        assert type(ws_connection) == Connection
        assert ws_connection.type == ConnectionTypes.AZURE_DATA_LAKE_GEN_2
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.SERVICE_PRINCIPAL)
        assert ws_connection.credentials.tenant_id == "1234"
        assert ws_connection.credentials.client_id == "12345"
        assert ws_connection.credentials.client_secret == "123456"
        assert ws_connection.credentials.authority_url == "https://login.microsoftonline.com"
        assert ws_connection.name == "test_gen2_conn1"
        assert ws_connection.target == "my_endpoint"
        assert ws_connection.tags["four"] == "five"
        # Auth url doesn't get copied back by rest conversion intentionally, so black it here
        # to simplify comparison.
        ws_connection.credentials.authority_url = ""
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/alds_gen2_entra.yaml")
        assert type(ws_connection) == Connection
        assert ws_connection.type == ConnectionTypes.AZURE_DATA_LAKE_GEN_2
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.AAD)
        assert ws_connection.name == "test_gen2_conn2"
        # Auth url doesn't get copied back by rest conversion intentionally, so black it here
        # to simplify comparison.
        ws_connection.credentials.authority_url = ""
        self.check_rest_conversion_stable(ws_connection)

    def test_one_lake(self):
        # Note: also tests SP credential.
        ws_connection = load_connection(source="./tests/test_configs/connection/one_lake_with_name.yaml")
        assert type(ws_connection) == MicrosoftOneLakeConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_ONE_LAKE)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.SERVICE_PRINCIPAL)
        assert ws_connection.credentials.tenant_id == "1234"
        assert ws_connection.credentials.client_id == "12345"
        assert ws_connection.credentials.client_secret == "123456"
        assert ws_connection.credentials.authority_url == "https://login.microsoftonline.com"
        assert ws_connection.name == "one_lake_with_name"
        assert ws_connection.target == "https://www.endpoint.com/the_workspace_name/my_lake_name.Lakehouse"
        # Auth url doesn't get copied back by rest conversion intentionally, so black it here
        # to simplify comparison.
        ws_connection.credentials.authority_url = ""
        self.check_rest_conversion_stable(ws_connection)

        # Note: also tests AAD credential
        ws_connection = load_connection(source="./tests/test_configs/connection/one_lake_with_id.yaml")
        assert type(ws_connection) == MicrosoftOneLakeConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_ONE_LAKE)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.AAD)
        assert ws_connection.name == "one_lake_with_id"
        assert ws_connection.target == "https://www.endpoint.com/the_workspace_name/1234567-1234-1234-1234-123456789012"
        self.check_rest_conversion_stable(ws_connection)

    def test_azure_open_ai(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/azure_open_ai_api.yaml")
        assert type(ws_connection) == AzureOpenAIConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_OPEN_AI)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert ws_connection.credentials.key == "12344"
        assert ws_connection.api_key == "12344"
        assert ws_connection.name == "test_ws_conn_open_ai"
        assert ws_connection.target == "dummy"
        assert ws_connection.tags["hello"] == "world"
        assert ws_connection.tags["ApiType"] == "Azure"
        assert ws_connection.api_version == "1.0"
        assert ws_connection.open_ai_resource_id == "some id"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/azure_open_ai_entra.yaml")
        assert type(ws_connection) == AzureOpenAIConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_OPEN_AI)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.AAD)
        assert ws_connection.name == "azure_open_ai_conn_entra"
        assert ws_connection.target == "dummy"
        assert ws_connection.tags["hello"] == "world"
        assert ws_connection.tags["ApiType"] == "Azure"
        assert ws_connection.api_version == "1.0"
        assert ws_connection.open_ai_resource_id is None
        self.check_rest_conversion_stable(ws_connection)

    def test_ai_services(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/ai_services_with_key.yaml")
        assert type(ws_connection) == AzureAIServiceConnection
        assert ws_connection.type == ConnectionTypes.AZURE_AI_SERVICES
        assert ws_connection.api_key == "2222"
        assert ws_connection.name == "ai_services_conn_api"
        assert ws_connection.target == "my_endpoint"
        assert ws_connection.ai_services_resource_id == "this-needs-to-be-a-valid-ai-services-id-in-e2e-tests"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/ai_services_with_entra.yaml")
        assert type(ws_connection) == AzureAIServiceConnection
        assert ws_connection.type == ConnectionTypes.AZURE_AI_SERVICES
        assert ws_connection.name == "ai_services_conn_entra"
        assert ws_connection.target == "my_endpoint"
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.AAD)
        assert ws_connection.ai_services_resource_id == "this-needs-to-be-a-valid-ai-services-id-in-e2e-tests"
        self.check_rest_conversion_stable(ws_connection)

    def test_content_safety(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/content_safety_with_key.yaml")
        assert type(ws_connection) == AzureContentSafetyConnection
        assert ws_connection.type == ConnectionTypes.AZURE_CONTENT_SAFETY
        assert ws_connection.tags["Kind"] == CognitiveServiceKinds.CONTENT_SAFETY
        assert ws_connection.api_key == "2222"
        assert ws_connection.name == "content_safety_conn_api"
        assert ws_connection.target == "my_endpoint"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/content_safety_with_entra.yaml")
        assert type(ws_connection) == AzureContentSafetyConnection
        assert ws_connection.type == ConnectionTypes.AZURE_CONTENT_SAFETY
        assert ws_connection.tags["Kind"] == CognitiveServiceKinds.CONTENT_SAFETY
        assert ws_connection.name == "content_safety_conn_entra"
        assert ws_connection.target == "my_endpoint"
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.AAD)
        self.check_rest_conversion_stable(ws_connection)

    def test_speech(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/speech_with_key.yaml")

        assert type(ws_connection) == AzureSpeechServicesConnection
        assert ws_connection.type == ConnectionTypes.AZURE_SPEECH_SERVICES
        assert ws_connection.tags["Kind"] == CognitiveServiceKinds.SPEECH
        assert ws_connection.api_key == "2222"
        assert ws_connection.name == "speech_api"
        assert ws_connection.target == "my_endpoint"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/speech_with_entra.yaml")
        assert type(ws_connection) == AzureSpeechServicesConnection
        assert ws_connection.type == ConnectionTypes.AZURE_SPEECH_SERVICES
        assert ws_connection.tags["Kind"] == CognitiveServiceKinds.SPEECH
        assert ws_connection.name == "speech_entra"
        assert ws_connection.target == "my_endpoint"
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.AAD)
        self.check_rest_conversion_stable(ws_connection)

    def test_search(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/search_with_key.yaml")
        assert type(ws_connection) == AzureAISearchConnection
        assert ws_connection.type == ConnectionTypes.AZURE_SEARCH
        assert ws_connection.api_key == "3333"
        assert ws_connection.name == "search_api"
        assert ws_connection.target == "this_is_a_target"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/search_with_entra.yaml")
        assert type(ws_connection) == AzureAISearchConnection
        assert ws_connection.type == ConnectionTypes.AZURE_SEARCH
        assert ws_connection.name == "search_entra"
        assert ws_connection.target == "this_is_a_target_too"
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.AAD)
        self.check_rest_conversion_stable(ws_connection)

    def test_api_key(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/api_key_conn.yaml")
        assert type(ws_connection) == APIKeyConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.API_KEY)
        assert ws_connection.api_key == "3232"
        assert ws_connection.name == "just_api"
        assert ws_connection.api_base == "this_is_a_target"
        self.check_rest_conversion_stable(ws_connection)

    def test_custom(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/custom.yaml")
        assert type(ws_connection) == Connection
        assert ws_connection.type == camel_to_snake(ConnectionTypes.CUSTOM)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert ws_connection.credentials.key == "4444"
        assert ws_connection.name == "test_ws_conn_custom_keys"
        assert ws_connection.target == "my_endpoint"
        assert ws_connection.tags["one"] == "two"
        self.check_rest_conversion_stable(ws_connection)

    def test_open_ai(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/not_azure_open_ai.yaml")
        assert type(ws_connection) == OpenAIConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.OPEN_AI)
        assert ws_connection.api_key == "123446"
        assert ws_connection.name == "open_ai_conn"
        assert ws_connection.target is None
        self.check_rest_conversion_stable(ws_connection)

    def test_serp(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/serp.yaml")
        assert type(ws_connection) == SerpConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.SERP)
        assert ws_connection.api_key == "1234467"
        assert ws_connection.name == "serp_conn"
        assert ws_connection.target is None
        self.check_rest_conversion_stable(ws_connection)

    def test_git(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/git_pat.yaml")

        assert type(ws_connection) == Connection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.GIT)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
        assert ws_connection.credentials.pat == "dummy_pat"
        assert ws_connection.name == "test_ws_conn_git_pat"
        assert ws_connection.target == "https://test-git-feed.com"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/git_no_cred.yaml")
        assert type(ws_connection) == Connection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.GIT)
        assert ws_connection.credentials.type == ConnectionAuthType.NONE
        assert ws_connection.name == "git_no_cred_conn"
        assert ws_connection.target == "https://test-git-feed.com2"
        self.check_rest_conversion_stable(ws_connection)

    def test_python_feed(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/python_feed_pat.yaml")
        assert type(ws_connection) == Connection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
        assert ws_connection.credentials.pat == "dummy_pat"
        assert ws_connection.name == "test_ws_conn_python_pat"
        assert ws_connection.target == "https://test-feed.com"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/python_feed_user_pass.yaml")
        assert type(ws_connection) == Connection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert ws_connection.credentials.username == "john"
        assert ws_connection.credentials.password == "halo"
        assert ws_connection.name == "test_ws_conn_python_user_pass"
        assert ws_connection.target == "https://test-feed.com2"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/python_feed_no_cred.yaml")
        assert type(ws_connection) == Connection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
        assert ws_connection.credentials.type == ConnectionAuthType.NONE
        assert ws_connection.name == "test_ws_conn_python_no_cred"
        assert ws_connection.target == "https://test-feed.com3"
        self.check_rest_conversion_stable(ws_connection)

    def test_container_registry(self):
        ws_connection = load_connection(
            source="./tests/test_configs/connection/container_registry_managed_identity.yaml"
        )
        assert ws_connection.type == camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.MANAGED_IDENTITY)
        assert ws_connection.credentials.client_id == "client_id"
        assert ws_connection.credentials.resource_id == "resource_id"
        assert ws_connection.name == "test_ws_conn_cr_managed"
        assert ws_connection.target == "https://test-feed.com"
        self.check_rest_conversion_stable(ws_connection)

        ws_connection = load_connection(source="./tests/test_configs/connection/container_registry_user_pass.yaml")
        assert ws_connection.type == camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert ws_connection.credentials.username == "springer"
        assert ws_connection.credentials.password == "spaniel"
        assert ws_connection.name == "test_ws_conn_cr_user_pass"
        assert ws_connection.target == "https://test-feed.com2"
        self.check_rest_conversion_stable(ws_connection)

    def test_serverless(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/serverless_api.yaml")

        assert type(ws_connection) == ServerlessConnection
        assert ws_connection.type == camel_to_snake(ConnectionCategory.SERVERLESS)
        assert ws_connection.api_key == "1029"
        assert ws_connection.name == "serverless_with_api"
        assert ws_connection.target == "serverless_endpoint"
        self.check_rest_conversion_stable(ws_connection)

    # Old connection tests. These have not had their valid credential inputs verified by any known recent spec.

    def test_s3_access_key(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/s3_access_key.yaml")

        assert ws_connection.type == camel_to_snake(ConnectionCategory.S3)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.ACCESS_KEY)
        assert ws_connection.credentials.access_key_id == "dummy"
        assert ws_connection.credentials.secret_access_key == "dummy"
        assert ws_connection.name == "test_ws_conn_s3"
        assert ws_connection.target == "dummy"
        assert ws_connection.tags == {}

    def test_snowflake(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/snowflake_user_pwd.yaml")

        assert ws_connection.type == camel_to_snake(ConnectionCategory.SNOWFLAKE)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert ws_connection.credentials.username == "dummy"
        assert ws_connection.credentials.password == "dummy"
        assert ws_connection.name == "test_ws_conn_snowflake"
        assert ws_connection.target == "dummy"
        assert ws_connection.tags == {}

    def test_azure_sql_db(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/azure_sql_db_user_pwd.yaml")

        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_SQL_DB)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert ws_connection.credentials.username == "dummy"
        assert ws_connection.credentials.password == "dummy"
        assert ws_connection.name == "test_ws_conn_azure_sql_db"
        assert ws_connection.target == "dummy"
        assert ws_connection.tags == {}

    def test_synapse_analytics(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/azure_synapse_analytics_user_pwd.yaml")

        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_SYNAPSE_ANALYTICS)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert ws_connection.credentials.username == "dummy"
        assert ws_connection.credentials.password == "dummy"
        assert ws_connection.name == "test_ws_conn_azure_synapse_analytics"
        assert ws_connection.target == "dummy"
        assert ws_connection.tags == {}

    def test_my_sql_db(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/azure_my_sql_db_user_pwd.yaml")

        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_MY_SQL_DB)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert ws_connection.credentials.username == "dummy"
        assert ws_connection.credentials.password == "dummy"
        assert ws_connection.name == "test_ws_conn_azure_my_sql_db"
        assert ws_connection.target == "dummy"
        assert ws_connection.tags == {}

    def test_postgres_db(self):
        ws_connection = load_connection(source="./tests/test_configs/connection/azure_postgres_db_user_pwd.yaml")

        assert ws_connection.type == camel_to_snake(ConnectionCategory.AZURE_POSTGRES_DB)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert ws_connection.credentials.username == "dummy"
        assert ws_connection.credentials.password == "dummy"
        assert ws_connection.name == "test_ws_conn_azure_postgres_db"
        assert ws_connection.target == "dummy"
        assert ws_connection.tags == {}

    def empty_credentials_rest_conversion(self):
        ws_connection = Connection(
            target="dummy_target",
            type=camel_to_snake(ConnectionCategory.PYTHON_FEED),
            credentials=None,
            name="dummy_connection",
            tags=None,
        )
        rest_conn = ws_connection._to_rest_object()
        new_ws_conn = AzureOpenAIConnection._from_rest_object(rest_obj=rest_conn)
        assert new_ws_conn.credentials == None

    def test_ws_conn_subtype_restriction(self):
        with pytest.raises(ValueError):
            _ = Connection(
                target="dummy_target",
                type=ConnectionCategory.AZURE_OPEN_AI,
                name="dummy_connection",
                strict_typing=True,
                credentials=None,
            )
        _ = AzureOpenAIConnection(
            target="dummy_target",
            name="dummy_connection",
            strict_typing=True,
            credentials=None,
        )

    def test_bad_credential_load_attempts(self):
        with pytest.raises(ValidationError):
            _ = load_connection(source="./tests/test_configs/connection/blob_store_bad_cred.yaml")

        with pytest.raises(ValueError):
            _ = Connection(
                name="bad",
                target="bad",
                type=ConnectionTypes.AZURE_DATA_LAKE_GEN_2,
                credentials=ApiKeyConfiguration(key="bad"),
            )
