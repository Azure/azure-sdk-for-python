# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import random
import re
import functools
import json
from typing import Optional, Any, Dict
from azure.ai.projects.models import (
    Connection,
    ConnectionType,
    CustomCredential,
    CredentialType,
    ApiKeyCredentials,
    Deployment,
    DeploymentType,
    ModelDeployment,
    Index,
    IndexType,
    AzureAISearchIndex,
    DatasetVersion,
    DatasetType,
    DatasetCredential,
    ItemResource,
    ItemType,
    ResponsesMessageRole,
    ItemContentType,
)
from azure.ai.projects.models._models import AgentObject, AgentVersionObject
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, is_live_and_not_recording
from azure.ai.projects import AIProjectClient as AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

# temporary requirements for recorded_by_proxy_httpx and recorded_by_proxy_async_httpx
import logging
import urllib.parse as url_parse

try:
    import httpx
except ImportError:
    httpx = None

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

from devtools_testutils import is_live_internal, is_live_and_not_recording, trim_kwargs_from_test_function
from devtools_testutils.proxy_testcase import (
    get_test_id,
    start_record_or_playback,
    stop_record_or_playback,
    get_proxy_netloc,
)

# Load secrets from environment variables
servicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_tests",
    azure_ai_projects_tests_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_projects_tests_agents_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_projects_tests_tracing_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_projects_tests_container_app_resource_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.App/containerApps/00000",
    azure_ai_projects_tests_container_ingress_subdomain_suffix="00000",
)


class TestBase(AzureRecordedTestCase):

    test_redteams_params = {
        # cSpell:disable-next-line
        "connection_name": "naposaniwestus3",
        "connection_type": ConnectionType.AZURE_OPEN_AI,
        "model_deployment_name": "gpt-4o-mini",
    }

    test_connections_params = {
        "connection_name": "custom_keys_connection",
        "connection_type": ConnectionType.CUSTOM,
    }

    test_deployments_params = {
        "model_publisher": "Cohere",
        "model_name": "gpt-4o",
        "model_deployment_name": "DeepSeek-V3",
    }

    test_agents_params = {
        "model_deployment_name": "gpt-4o",
        "agent_name": "agent-for-python-projects-sdk-testing",
    }

    test_inference_params = {
        "connection_name_api_key_auth": "connection1",
        "connection_name_entra_id_auth": "connection2",
        "model_deployment_name": "gpt-4o",
        "aoai_api_version": "2025-04-01-preview",
    }

    test_indexes_params = {
        "index_name": f"test-index-name",
        "index_version": "1",
        "ai_search_connection_name": "my-ai-search-connection",
        "ai_search_index_name": "my-ai-search-index",
    }

    test_datasets_params = {
        "dataset_name_1": f"test-dataset-name-{random.randint(0, 99999):05d}",
        "dataset_name_2": f"test-dataset-name-{random.randint(0, 99999):05d}",
        "dataset_name_3": f"test-dataset-name-{random.randint(0, 99999):05d}",
        "dataset_name_4": f"test-dataset-name-{random.randint(0, 99999):05d}",
        "dataset_version": 1,
        "connection_name": "balapvbyostoragecanary",
    }

    test_files_params = {
        "test_file_name": "test_file.jsonl",
        "file_purpose": "fine-tune",
    }

    test_finetuning_params = {
        "sft": {
            "openai": {
                "model_name": "gpt-4.1",
                "deployment": {
                    "deployment_name": "gpt-4-1-fine-tuned-test",
                    "pre_finetuned_model": "ft:gpt-4.1:azure-ai-test::ABCD1234",
                },
            },
            "oss": {"model_name": "Ministral-3B"},
            "training_file_name": "sft_training_set.jsonl",
            "validation_file_name": "sft_validation_set.jsonl",
        },
        "dpo": {
            "openai": {"model_name": "gpt-4o-mini"},
            "training_file_name": "dpo_training_set.jsonl",
            "validation_file_name": "dpo_validation_set.jsonl",
        },
        "rft": {
            "openai": {"model_name": "o4-mini"},
            "training_file_name": "rft_training_set.jsonl",
            "validation_file_name": "rft_validation_set.jsonl",
        },
        "n_epochs": 1,
        "batch_size": 1,
        "learning_rate_multiplier": 1.0,
    }

    # Regular expression describing the pattern of an Application Insights connection string.
    REGEX_APPINSIGHTS_CONNECTION_STRING = re.compile(
        r"^InstrumentationKey=[0-9a-fA-F-]{36};IngestionEndpoint=https://.+.applicationinsights.azure.com/;LiveEndpoint=https://.+.monitor.azure.com/;ApplicationId=[0-9a-fA-F-]{36}$"
    )

    # helper function: create projects client using environment variables
    def create_client(self, *, operation_group: Optional[str] = None, **kwargs) -> AIProjectClient:
        # fetch environment variables
        project_endpoint_env_variable = (
            f"azure_ai_projects_tests_{operation_group}_project_endpoint"
            if operation_group
            else "azure_ai_projects_tests_project_endpoint"
        )
        endpoint = kwargs.pop(project_endpoint_env_variable)
        credential = self.get_credential(AIProjectClient, is_async=False)

        # create and return client
        client = AIProjectClient(
            endpoint=endpoint,
            credential=credential,
        )

        return client

    # helper function: create async projects client using environment variables
    def create_async_client(self, *, operation_group: Optional[str] = None, **kwargs) -> AsyncAIProjectClient:
        # fetch environment variables
        project_endpoint_env_variable = (
            f"azure_ai_projects_tests_{operation_group}_project_endpoint"
            if operation_group
            else "azure_ai_projects_tests_project_endpoint"
        )
        endpoint = kwargs.pop(project_endpoint_env_variable)
        credential = self.get_credential(AsyncAIProjectClient, is_async=True)

        # create and return async client
        client = AsyncAIProjectClient(
            endpoint=endpoint,
            credential=credential,
        )

        return client

    @staticmethod
    def assert_equal_or_not_none(actual, expected=None):
        assert actual is not None
        if expected is not None:
            assert actual == expected

    # Checks that a given dictionary has at least one non-empty (non-whitespace) string key-value pair.
    @classmethod
    def is_valid_dict(cls, d: dict[str, str]) -> bool:
        return bool(d) and all(
            isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip() for k, v in d.items()
        )

    @classmethod
    def validate_connection(
        cls,
        connection: Connection,
        include_credentials: bool,
        *,
        expected_connection_type: Optional[ConnectionType] = None,
        expected_connection_name: Optional[str] = None,
        expected_authentication_type: Optional[CredentialType] = None,
        expected_is_default: Optional[bool] = None,
    ):
        assert connection.id is not None

        TestBase.assert_equal_or_not_none(connection.name, expected_connection_name)
        TestBase.assert_equal_or_not_none(connection.type, expected_connection_type)
        TestBase.assert_equal_or_not_none(connection.credentials.type, expected_authentication_type)

        if expected_is_default is not None:
            assert connection.is_default == expected_is_default

        if isinstance(connection.credentials, ApiKeyCredentials):
            assert connection.credentials.type == CredentialType.API_KEY
            if include_credentials:
                assert connection.credentials.api_key is not None
        elif isinstance(connection.credentials, CustomCredential):
            assert connection.credentials.type == CredentialType.CUSTOM
            if include_credentials:
                assert TestBase.is_valid_dict(connection.credentials.credential_keys)

    @classmethod
    def validate_red_team_response(
        cls, response, expected_attack_strategies: int = -1, expected_risk_categories: int = -1
    ):
        """Assert basic red team scan response properties."""
        assert response is not None
        assert hasattr(response, "name")
        assert hasattr(response, "display_name")
        assert hasattr(response, "status")
        assert hasattr(response, "attack_strategies")
        assert hasattr(response, "risk_categories")
        assert hasattr(response, "target")
        assert hasattr(response, "properties")

        # Validate attack strategies and risk categories
        if expected_attack_strategies != -1:
            assert len(response.attack_strategies) == expected_attack_strategies
        if expected_risk_categories != -1:
            assert len(response.risk_categories) == expected_risk_categories
        assert response.status is not None
        cls._assert_azure_ml_properties(response)

    @classmethod
    def _assert_azure_ml_properties(cls, response):
        """Assert Azure ML specific properties are present and valid."""
        properties = response.properties
        assert properties is not None, "Red team scan properties should not be None"

        required_properties = [
            "runType",
            "redteaming",
            "_azureml.evaluation_run",
            "_azureml.evaluate_artifacts",
            "AiStudioEvaluationUri",
        ]

        for prop in required_properties:
            assert prop in properties, f"Missing required property: {prop}"

        # Validate specific property values
        assert properties["runType"] == "eval_run"
        assert properties["_azureml.evaluation_run"] == "evaluation.service"
        assert "instance_results.json" in properties["_azureml.evaluate_artifacts"]
        assert properties["redteaming"] == "asr"

        # Validate AI Studio URI format
        ai_studio_uri = properties["AiStudioEvaluationUri"]
        assert ai_studio_uri.startswith("https://ai.azure.com/resource/build/redteaming/")
        assert "wsid=" in ai_studio_uri
        assert "tid=" in ai_studio_uri

    @classmethod
    def validate_deployment(
        cls,
        deployment: Deployment,
        *,
        expected_model_name: Optional[str] = None,
        expected_model_deployment_name: Optional[str] = None,
        expected_model_publisher: Optional[str] = None,
    ):
        assert type(deployment) == ModelDeployment
        assert deployment.type == DeploymentType.MODEL_DEPLOYMENT
        assert deployment.model_version is not None
        # Comment out the below, since I see that `Cohere-embed-v3-english` has an empty capabilities dict.
        # assert TestBase.is_valid_dict(deployment.capabilities)
        assert bool(deployment.sku)  # Check none-empty

        TestBase.assert_equal_or_not_none(deployment.model_name, expected_model_name)
        TestBase.assert_equal_or_not_none(deployment.name, expected_model_deployment_name)
        TestBase.assert_equal_or_not_none(deployment.model_publisher, expected_model_publisher)

    @classmethod
    def validate_index(
        cls,
        index: Index,
        *,
        expected_index_type: Optional[IndexType] = None,
        expected_index_name: Optional[str] = None,
        expected_index_version: Optional[str] = None,
        expected_ai_search_connection_name: Optional[str] = None,
        expected_ai_search_index_name: Optional[str] = None,
    ):

        TestBase.assert_equal_or_not_none(index.name, expected_index_name)
        TestBase.assert_equal_or_not_none(index.version, expected_index_version)

        if expected_index_type == IndexType.AZURE_SEARCH:
            assert type(index) == AzureAISearchIndex
            assert index.type == IndexType.AZURE_SEARCH
            TestBase.assert_equal_or_not_none(index.connection_name, expected_ai_search_connection_name)
            TestBase.assert_equal_or_not_none(index.index_name, expected_ai_search_index_name)

    @classmethod
    def validate_dataset(
        cls,
        dataset: DatasetVersion,
        *,
        expected_dataset_type: Optional[DatasetType] = None,
        expected_dataset_name: Optional[str] = None,
        expected_dataset_version: Optional[str] = None,
        expected_connection_name: Optional[str] = None,
    ):
        assert dataset.data_uri is not None

        if expected_dataset_type:
            assert dataset.type == expected_dataset_type
        else:
            assert dataset.type == DatasetType.URI_FILE or dataset.type == DatasetType.URI_FOLDER

        TestBase.assert_equal_or_not_none(dataset.name, expected_dataset_name)
        TestBase.assert_equal_or_not_none(dataset.version, expected_dataset_version)
        if expected_connection_name:
            assert dataset.connection_name == expected_connection_name

    @classmethod
    def validate_dataset_credential(cls, dataset_credential: DatasetCredential):

        assert dataset_credential.blob_reference is not None
        assert dataset_credential.blob_reference.blob_uri
        assert dataset_credential.blob_reference.storage_account_arm_id

        assert dataset_credential.blob_reference.credential is not None
        assert (
            dataset_credential.blob_reference.credential.type == "SAS"
        )  # Why is this not of type CredentialType.SAS as defined for Connections?
        assert dataset_credential.blob_reference.credential.sas_uri

    @staticmethod
    def _validate_conversation(
        conversation: Any, *, expected_id: Optional[str] = None, expected_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        assert conversation.id
        assert conversation.created_at
        if expected_id is not None:
            assert conversation.id == expected_id
        if expected_metadata is not None:
            assert conversation.metadata == expected_metadata
        print(f"Conversation validated (id: {conversation.id})")

    def _validate_agent_version(
        self, agent: AgentVersionObject, expected_name: Optional[str] = None, expected_version: Optional[str] = None
    ) -> None:
        assert agent is not None
        assert isinstance(agent, AgentVersionObject)
        assert agent.id is not None
        if expected_name:
            assert agent.name == expected_name
        if expected_version:
            assert agent.version == expected_version
        print(f"Agent version validated (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    def _validate_agent(
        self, agent: AgentObject, expected_name: Optional[str] = None, expected_latest_version: Optional[str] = None
    ) -> None:
        assert agent is not None
        assert isinstance(agent, AgentObject)
        assert agent.id is not None
        if expected_name:
            assert agent.name == expected_name
        if expected_latest_version:
            assert agent.versions.latest.version == expected_latest_version
        print(f"Agent validated (id: {agent.id}, name: {agent.name}, latest version: {agent.versions.latest.version})")

    def _validate_conversation_item(
        self,
        item: ItemResource,
        *,
        expected_type: Optional[ItemType] = None,
        expected_id: Optional[str] = None,
        expected_role: Optional[ResponsesMessageRole] = None,
        expected_content_type: Optional[ItemContentType] = None,
        expected_content_text: Optional[str] = None,
    ) -> None:
        assert item

        # From ItemResource:
        if expected_type:
            assert item.type == expected_type
        else:
            assert item.type
        if expected_id:
            assert item.id == expected_id
        else:
            assert item.id

        # From ResponsesMessageItemResource:
        if expected_type == ItemType.MESSAGE:
            assert item.status == "completed"
            if expected_role:
                assert item.role == expected_role
            else:
                assert item.role

            # From ResponsesAssistantMessageItemResource, ResponsesDeveloperMessageItemResource, ResponsesSystemMessageItemResource, ResponsesUserMessageItemResource:
            assert len(item.content) == 1

            # From ItemContent:
            if expected_content_type:
                assert item.content[0].type == expected_content_type
            if expected_content_text:
                assert item.content[0].text == expected_content_text
        print(
            f"Conversation item validated (id: {item.id}, type: {item.type}, role: {item.role if item.type == ItemType.MESSAGE else 'N/A'})"
        )

    @classmethod
    def validate_file(
        cls,
        file_obj,
        *,
        expected_file_id: Optional[str] = None,
        expected_filename: Optional[str] = None,
        expected_purpose: Optional[str] = None,
    ):
        assert file_obj is not None
        assert file_obj.id is not None
        assert file_obj.bytes is not None
        assert file_obj.created_at is not None
        assert file_obj.filename is not None
        assert file_obj.purpose is not None

        TestBase.assert_equal_or_not_none(file_obj.id, expected_file_id)
        TestBase.assert_equal_or_not_none(file_obj.filename, expected_filename)
        TestBase.assert_equal_or_not_none(file_obj.purpose, expected_purpose)

    @classmethod
    def validate_fine_tuning_job(
        cls,
        job_obj,
        *,
        expected_job_id: Optional[str] = None,
        expected_model: Optional[str] = None,
        expected_status: Optional[str] = None,
    ):
        assert job_obj is not None
        assert job_obj.id is not None
        assert job_obj.model is not None
        assert job_obj.created_at is not None
        assert job_obj.status is not None
        assert job_obj.training_file is not None

        TestBase.assert_equal_or_not_none(job_obj.id, expected_job_id)
        TestBase.assert_equal_or_not_none(job_obj.model, expected_model)
        TestBase.assert_equal_or_not_none(job_obj.status, expected_status)

    def _request_callback(self, pipeline_request) -> None:
        self.pipeline_request = pipeline_request

    @staticmethod
    def _are_json_equal(json_str1: str, json_str2: str) -> bool:
        try:
            obj1 = json.loads(json_str1)
            obj2 = json.loads(json_str2)
            return obj1 == obj2
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return False


# The following two decorators recorded_by_proxy_httpx and recorded_by_proxy_async_httpx will be supplanted as part of #43794.
# These are provided here temporarily to support existing tests that use httpx-based clients until they can be migrated.
def recorded_by_proxy_httpx(test_func):
    """Decorator that redirects httpx network requests to target the azure-sdk-tools test proxy.

    Use this decorator for tests that use httpx-based clients (like OpenAI SDK) instead of Azure SDK clients.
    It monkeypatches httpx.HTTPTransport.handle_request to route requests through the test proxy.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#write-or-run-tests
    """
    if httpx is None:
        raise ImportError("httpx is required to use recorded_by_proxy_httpx. Install it with: pip install httpx")

    def record_wrap(*args, **kwargs):
        def transform_httpx_request(request: httpx.Request, recording_id: str) -> None:
            """Transform an httpx.Request to route through the test proxy."""
            parsed_result = url_parse.urlparse(str(request.url))

            # Store original upstream URI
            if "x-recording-upstream-base-uri" not in request.headers:
                request.headers["x-recording-upstream-base-uri"] = f"{parsed_result.scheme}://{parsed_result.netloc}"

            # Set recording headers
            request.headers["x-recording-id"] = recording_id
            request.headers["x-recording-mode"] = "record" if is_live_internal() else "playback"

            # Remove all request headers that start with `x-stainless`, since they contain CPU info, OS info, etc.
            # Those change depending on which machine the tests are run on, so we cannot have a single test recording with those.
            headers_to_remove = [key for key in request.headers.keys() if key.lower().startswith("x-stainless")]
            for header in headers_to_remove:
                del request.headers[header]

            # Rewrite URL to proxy
            updated_target = parsed_result._replace(**get_proxy_netloc()).geturl()
            request.url = httpx.URL(updated_target)

        def restore_httpx_response_url(response: httpx.Response) -> httpx.Response:
            """Restore the response's request URL to the original upstream target."""
            try:
                parsed_resp = url_parse.urlparse(str(response.request.url))
                upstream_uri_str = response.request.headers.get("x-recording-upstream-base-uri", "")
                if upstream_uri_str:
                    upstream_uri = url_parse.urlparse(upstream_uri_str)
                    original_target = parsed_resp._replace(
                        scheme=upstream_uri.scheme or parsed_resp.scheme, netloc=upstream_uri.netloc
                    ).geturl()
                    response.request.url = httpx.URL(original_target)
            except Exception:
                # Best-effort restore; don't fail the call if something goes wrong
                pass
            return response

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(test_func, trimmed_kwargs)

        if is_live_and_not_recording():
            return test_func(*args, **trimmed_kwargs)

        test_id = get_test_id()
        recording_id, variables = start_record_or_playback(test_id)
        original_transport_func = httpx.HTTPTransport.handle_request

        def combined_call(transport_self, request: httpx.Request) -> httpx.Response:
            transform_httpx_request(request, recording_id)
            result = original_transport_func(transport_self, request)
            return restore_httpx_response_url(result)

        httpx.HTTPTransport.handle_request = combined_call

        # Call the test function
        test_variables = None
        test_run = False
        try:
            try:
                test_variables = test_func(*args, variables=variables, **trimmed_kwargs)
                test_run = True
            except TypeError as error:
                if "unexpected keyword argument" in str(error) and "variables" in str(error):
                    logger = logging.getLogger()
                    logger.info(
                        "This test can't accept variables as input. The test method should accept `**kwargs` and/or a "
                        "`variables` parameter to make use of recorded test variables."
                    )
                else:
                    raise error
            # If the test couldn't accept `variables`, run without passing them
            if not test_run:
                test_variables = test_func(*args, **trimmed_kwargs)

        except ResourceNotFoundError as error:
            error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
            message = error_body.get("message") or error_body.get("Message")
            error_with_message = ResourceNotFoundError(message=message, response=error.response)
            raise error_with_message from error

        finally:
            httpx.HTTPTransport.handle_request = original_transport_func
            stop_record_or_playback(test_id, recording_id, test_variables)

        return test_variables

    return record_wrap


def recorded_by_proxy_async_httpx(test_func):
    """Decorator that redirects async httpx network requests to target the azure-sdk-tools test proxy.

    Use this decorator for async tests that use httpx-based clients (like OpenAI AsyncOpenAI SDK)
    instead of Azure SDK clients. It monkeypatches httpx.AsyncHTTPTransport.handle_async_request
    to route requests through the test proxy.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#write-or-run-tests
    """
    if httpx is None:
        raise ImportError("httpx is required to use recorded_by_proxy_async_httpx. Install it with: pip install httpx")

    async def record_wrap(*args, **kwargs):
        def transform_httpx_request(request: httpx.Request, recording_id: str) -> None:
            """Transform an httpx.Request to route through the test proxy."""
            parsed_result = url_parse.urlparse(str(request.url))

            # Store original upstream URI
            if "x-recording-upstream-base-uri" not in request.headers:
                request.headers["x-recording-upstream-base-uri"] = f"{parsed_result.scheme}://{parsed_result.netloc}"

            # Set recording headers
            request.headers["x-recording-id"] = recording_id
            request.headers["x-recording-mode"] = "record" if is_live_internal() else "playback"

            # Remove all request headers that start with `x-stainless`, since they contain CPU info, OS info, etc.
            # Those change depending on which machine the tests are run on, so we cannot have a single test recording with those.
            headers_to_remove = [key for key in request.headers.keys() if key.lower().startswith("x-stainless")]
            for header in headers_to_remove:
                del request.headers[header]

            # Rewrite URL to proxy
            updated_target = parsed_result._replace(**get_proxy_netloc()).geturl()
            request.url = httpx.URL(updated_target)

        def restore_httpx_response_url(response: httpx.Response) -> httpx.Response:
            """Restore the response's request URL to the original upstream target."""
            try:
                parsed_resp = url_parse.urlparse(str(response.request.url))
                upstream_uri_str = response.request.headers.get("x-recording-upstream-base-uri", "")
                if upstream_uri_str:
                    upstream_uri = url_parse.urlparse(upstream_uri_str)
                    original_target = parsed_resp._replace(
                        scheme=upstream_uri.scheme or parsed_resp.scheme, netloc=upstream_uri.netloc
                    ).geturl()
                    response.request.url = httpx.URL(original_target)
            except Exception:
                # Best-effort restore; don't fail the call if something goes wrong
                pass
            return response

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(test_func, trimmed_kwargs)

        if is_live_and_not_recording():
            return await test_func(*args, **trimmed_kwargs)

        test_id = get_test_id()
        recording_id, variables = start_record_or_playback(test_id)
        original_transport_func = httpx.AsyncHTTPTransport.handle_async_request

        async def combined_call(transport_self, request: httpx.Request) -> httpx.Response:
            transform_httpx_request(request, recording_id)
            result = await original_transport_func(transport_self, request)
            return restore_httpx_response_url(result)

        httpx.AsyncHTTPTransport.handle_async_request = combined_call

        # Call the test function
        test_variables = None
        test_run = False
        try:
            try:
                test_variables = await test_func(*args, variables=variables, **trimmed_kwargs)
                test_run = True
            except TypeError as error:
                if "unexpected keyword argument" in str(error) and "variables" in str(error):
                    logger = logging.getLogger()
                    logger.info(
                        "This test can't accept variables as input. The test method should accept `**kwargs` and/or a "
                        "`variables` parameter to make use of recorded test variables."
                    )
                else:
                    raise error
            # If the test couldn't accept `variables`, run without passing them
            if not test_run:
                test_variables = await test_func(*args, **trimmed_kwargs)

        except ResourceNotFoundError as error:
            error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
            message = error_body.get("message") or error_body.get("Message")
            error_with_message = ResourceNotFoundError(message=message, response=error.response)
            raise error_with_message from error

        finally:
            httpx.AsyncHTTPTransport.handle_async_request = original_transport_func
            stop_record_or_playback(test_id, recording_id, test_variables)

        return test_variables

    return record_wrap
