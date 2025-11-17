import pytest
import yaml
import json
import copy
import sys
from test_utilities.utils import verify_entity_load_and_dump
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    OnlineEndpointData,
    EndpointAuthKeys as RestEndpointAuthKeys,
    EndpointAuthToken as RestEndpointAuthToken,
)
from azure.ai.ml._restclient.v2023_10_01.models import BatchEndpoint as BatchEndpointData
from azure.ai.ml import load_batch_endpoint, load_online_endpoint
from azure.ai.ml.entities import (
    BatchEndpoint,
    ManagedOnlineEndpoint,
    KubernetesOnlineEndpoint,
    OnlineEndpoint,
    EndpointAuthKeys,
    EndpointAuthToken,
)
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.production_experiences_test
@pytest.mark.unittest
class TestOnlineEndpointYAML:
    SIMPLE_ENDPOINT_WITH_BLUE_BAD = "tests/test_configs/endpoints/online/online_endpoint_create_aks_bad.yml"
    MINIMAL_ENDPOINT = "tests/test_configs/endpoints/online/online_endpoint_minimal.yaml"
    MINIMAL_DEPLOYMENT = "tests/test_configs/deployments/online/online_endpoint_deployment_k8s_minimum.yml"
    ONLINE_ENDPOINT_REST = "tests/test_configs/endpoints/online/online_endpoint_rest.json"

    def test_specific_endpoint_load_and_dump(self) -> None:
        with open(TestOnlineEndpointYAML.MINIMAL_ENDPOINT, "r") as f:
            target = yaml.safe_load(f)

        def simple_online_endpoint_validation(endpoint):
            assert isinstance(endpoint, OnlineEndpoint)
            assert endpoint.name == target["name"]

        _ = verify_entity_load_and_dump(
            load_online_endpoint,
            simple_online_endpoint_validation,
            TestOnlineEndpointYAML.MINIMAL_ENDPOINT,
            test_dump_file_path=None,
        )

    def test_default_endpoint_load_to_online(self) -> None:
        with open(TestOnlineEndpointYAML.MINIMAL_ENDPOINT, "r") as f:
            target = yaml.safe_load(f)
        endpoint = load_online_endpoint(TestOnlineEndpointYAML.MINIMAL_ENDPOINT)
        assert isinstance(endpoint, OnlineEndpoint)
        assert endpoint.name == target["name"]

    def test_online_endpoint_to_rest_object_with_no_issue(self) -> None:
        endpoint = load_online_endpoint(TestOnlineEndpointYAML.MINIMAL_ENDPOINT)
        endpoint._to_rest_online_endpoint("westus2")

    def test_from_rest_object_kubenetes(self) -> None:
        with open(TestOnlineEndpointYAML.ONLINE_ENDPOINT_REST, "r") as f:
            online_deployment_rest = OnlineEndpointData.deserialize(json.load(f))
            online_endpoint = OnlineEndpoint._from_rest_object(online_deployment_rest)
            assert isinstance(online_endpoint, KubernetesOnlineEndpoint)
            assert online_endpoint.name == online_deployment_rest.name
            assert online_endpoint.compute == online_deployment_rest.properties.compute
            assert online_endpoint.tags == online_deployment_rest.tags
            assert online_endpoint.traffic == online_deployment_rest.properties.traffic
            assert online_endpoint.description == online_deployment_rest.properties.description
            assert online_endpoint.provisioning_state == online_deployment_rest.properties.provisioning_state
            assert online_endpoint.identity.type == "system_assigned"
            assert online_endpoint.identity.principal_id == online_deployment_rest.identity.principal_id
            assert online_endpoint.properties["createdBy"] == online_deployment_rest.system_data.created_by

    def test_from_rest_object_managed(self) -> None:
        with open(TestOnlineEndpointYAML.ONLINE_ENDPOINT_REST, "r") as f:
            online_deployment_rest = OnlineEndpointData.deserialize(json.load(f))
            online_deployment_rest.properties.compute = None
            online_endpoint = OnlineEndpoint._from_rest_object(online_deployment_rest)
            assert isinstance(online_endpoint, ManagedOnlineEndpoint)
            assert online_endpoint.name == online_deployment_rest.name
            assert online_endpoint.tags == online_deployment_rest.tags
            assert online_endpoint.traffic == online_deployment_rest.properties.traffic
            assert online_endpoint.description == online_deployment_rest.properties.description
            assert online_endpoint.provisioning_state == online_deployment_rest.properties.provisioning_state
            assert online_endpoint.identity.type == "system_assigned"
            assert online_endpoint.identity.principal_id == online_deployment_rest.identity.principal_id
            assert online_endpoint.properties["createdBy"] == online_deployment_rest.system_data.created_by


@pytest.mark.unittest
class TestBatchEndpointYAML:
    BATCH_ENDPOINT_WITH_BLUE = "tests/test_configs/endpoints/batch/batch_endpoint.yaml"
    BATCH_ENDPOINT_REST = "tests/test_configs/endpoints/batch/batch_endpoint_rest.json"

    def test_generic_endpoint_load_and_dump_2(self) -> None:
        with open(TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE, "r") as f:
            target = yaml.safe_load(f)

        def simple_batch_endpoint_validation(endpoint):
            assert isinstance(endpoint, BatchEndpoint)
            assert endpoint.name == target["name"].lower()
            assert endpoint.description == target["description"]
            assert endpoint.auth_mode == target["auth_mode"]

        verify_entity_load_and_dump(
            load_batch_endpoint,
            simple_batch_endpoint_validation,
            TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE,
            test_dump_file_path=None,
        )

    def test_to_rest_batch_endpoint(self) -> None:
        with open(TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE, "r") as f:
            target = yaml.safe_load(f)
        endpoint = load_batch_endpoint(TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE)
        rest_batch_endpoint = endpoint._to_rest_batch_endpoint("master")

        assert rest_batch_endpoint.tags
        assert len(rest_batch_endpoint.tags)
        assert rest_batch_endpoint.tags == target["tags"]

    def test_to_dict(self) -> None:
        endpoint = load_batch_endpoint(TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE)
        endpoint_dict = endpoint._to_dict()

        assert endpoint_dict["name"] == endpoint.name
        assert endpoint_dict["description"] == endpoint.description
        assert endpoint_dict["auth_mode"] == endpoint.auth_mode
        assert endpoint_dict["tags"] == endpoint.tags
        assert endpoint_dict["auth_mode"] == "aad_token"
        assert endpoint_dict["properties"] == endpoint.properties

    def test_from_rest(self) -> None:
        with open(TestBatchEndpointYAML.BATCH_ENDPOINT_REST, "r") as f:
            batch_endpoint_rest = BatchEndpointData.deserialize(json.load(f))
            batch_endpoint = BatchEndpoint._from_rest_object(batch_endpoint_rest)
            assert batch_endpoint.name == batch_endpoint_rest.name
            assert batch_endpoint.id == batch_endpoint_rest.id
            assert batch_endpoint.tags == batch_endpoint_rest.tags
            assert batch_endpoint.properties == batch_endpoint_rest.properties.properties
            assert batch_endpoint.auth_mode == "aad_token"
            assert batch_endpoint.description == batch_endpoint_rest.properties.description
            assert batch_endpoint.location == batch_endpoint_rest.location
            assert batch_endpoint.provisioning_state == batch_endpoint_rest.properties.provisioning_state
            assert batch_endpoint.scoring_uri == batch_endpoint_rest.properties.scoring_uri
            assert batch_endpoint.openapi_uri == batch_endpoint_rest.properties.swagger_uri

    def test_batch_endpoint_with_deployment_name_promoted_param_only(self) -> None:
        endpoint = BatchEndpoint(
            name="my-batch-endpoint",
            description="this is a sample batch endpoint",
            defaults={"deployment_name": "gg"},
            default_deployment_name="fff",
            # badParam="I should not break", until it is fixed in SDK
            tags={"foo": "bar"},
        )

        assert endpoint.defaults["deployment_name"] == "gg"

    def test_batch_endpoint_with_deployment_name_promoted_param_and_main_param(self) -> None:
        endpoint = BatchEndpoint(
            name="my-batch-endpoint",
            description="this is a sample batch endpoint",
            default_deployment_name="fff",
            # badParam="I should not break", until it is fixed in SDK
            tags={"foo": "bar"},
        )

        assert endpoint.defaults["deployment_name"] == "fff"

    def test_batch_endpoint_with_deployment_no_defaults(self) -> None:
        endpoint = BatchEndpoint(
            name="my-batch-endpoint",
            description="this is a sample batch endpoint",
            # badParam="I should not break", until it is fixed in SDK
            tags={"foo": "bar"},
        )

        assert endpoint.defaults is None


class TestKubernetesOnlineEndopint:
    K8S_ONLINE_ENDPOINT = "tests/test_configs/endpoints/online/online_endpoint_create_k8s.yml"

    def test_merge_with(self) -> None:
        online_endpoint = load_online_endpoint(TestKubernetesOnlineEndopint.K8S_ONLINE_ENDPOINT)
        other_online_endpoint = copy.deepcopy(online_endpoint)
        other_online_endpoint.compute = "k8ecompute"
        other_online_endpoint.tags = {"tag3": "value3"}
        other_online_endpoint.traffic = {"blue": 90, "green": 10}
        other_online_endpoint.description = "new description"
        other_online_endpoint.mirror_traffic = {"blue": 30}
        other_online_endpoint.auth_mode = "aml_token"
        other_online_endpoint.properties = {"some-prop": "value"}

        online_endpoint._merge_with(other_online_endpoint)

        assert isinstance(online_endpoint, KubernetesOnlineEndpoint)
        assert online_endpoint.compute == "k8ecompute"
        assert online_endpoint.tags == {"tag1": "value1", "tag2": "value2", "tag3": "value3"}
        assert online_endpoint.description == "new description"
        assert online_endpoint.traffic == {"blue": 90, "green": 10}
        assert online_endpoint.mirror_traffic == {"blue": 30}
        assert online_endpoint.auth_mode == "aml_token"
        assert online_endpoint.properties == {"some-prop": "value"}

    def test_merge_with_throws_exception_when_name_masmatch(self) -> None:
        online_endpoint = load_online_endpoint(TestKubernetesOnlineEndopint.K8S_ONLINE_ENDPOINT)
        other_online_endpoint = copy.deepcopy(online_endpoint)
        other_online_endpoint.name = "new_name"

        with pytest.raises(ValidationException) as ex:
            online_endpoint._merge_with(other_online_endpoint)
        assert (
            ex.value.exc_msg
            == "The endpoint name: k8se2etest and new_name are not matched when merging., NoneType: None"
        )

    def test_to_rest_online_endpoint(self) -> None:
        online_endpoint = load_online_endpoint(TestKubernetesOnlineEndopint.K8S_ONLINE_ENDPOINT)
        online_endpoint.public_network_access = "Enabled"
        online_endpoint_rest = online_endpoint._to_rest_online_endpoint("westus2")
        assert online_endpoint_rest.tags == online_endpoint.tags
        assert online_endpoint_rest.properties.compute == online_endpoint.compute
        assert online_endpoint_rest.properties.traffic == online_endpoint.traffic
        assert online_endpoint_rest.properties.description == online_endpoint.description
        assert online_endpoint_rest.properties.mirror_traffic == online_endpoint.mirror_traffic
        assert online_endpoint_rest.properties.auth_mode.lower() == online_endpoint.auth_mode
        assert online_endpoint_rest.location == "westus2"
        assert online_endpoint_rest.identity.type == "SystemAssigned"
        assert online_endpoint_rest.properties.public_network_access == online_endpoint.public_network_access

    def test_to_rest_online_endpoint_when_identity_none(self) -> None:
        online_endpoint = load_online_endpoint(TestKubernetesOnlineEndopint.K8S_ONLINE_ENDPOINT)
        online_endpoint.identity = None
        online_endpoint_rest = online_endpoint._to_rest_online_endpoint("westus2")
        assert online_endpoint_rest.tags == online_endpoint.tags
        assert online_endpoint_rest.properties.compute == online_endpoint.compute
        assert online_endpoint_rest.properties.traffic == online_endpoint.traffic
        assert online_endpoint_rest.properties.description == online_endpoint.description
        assert online_endpoint_rest.properties.mirror_traffic == online_endpoint.mirror_traffic
        assert online_endpoint_rest.properties.auth_mode.lower() == online_endpoint.auth_mode
        assert online_endpoint_rest.location == "westus2"
        assert online_endpoint_rest.identity.type == "SystemAssigned"

    def test_to_rest_online_endpoint_raise_exception_identity_type_none(self) -> None:
        online_endpoint = load_online_endpoint(TestKubernetesOnlineEndopint.K8S_ONLINE_ENDPOINT)
        online_endpoint.identity.type = None
        with pytest.raises(ValidationException) as ex:
            online_endpoint._to_rest_online_endpoint("westus2")
        assert str(ex.value) == "Identity type not found in provided yaml file."

    def test_to_rest_online_endpoint_traffic_update(self) -> None:
        online_endpoint = load_online_endpoint(TestKubernetesOnlineEndopint.K8S_ONLINE_ENDPOINT)
        online_endpoint_rest = online_endpoint._to_rest_online_endpoint_traffic_update("westus2")
        assert online_endpoint_rest.location == "westus2"
        assert online_endpoint_rest.tags == online_endpoint.tags
        assert online_endpoint_rest.identity.type == "system_assigned"
        assert online_endpoint_rest.properties.compute == online_endpoint.compute
        assert online_endpoint_rest.properties.description == online_endpoint.description
        assert online_endpoint_rest.properties.auth_mode.lower() == online_endpoint.auth_mode
        assert online_endpoint_rest.properties.traffic == online_endpoint.traffic

    def test_to_dict(self) -> None:
        online_endpoint = load_online_endpoint(TestKubernetesOnlineEndopint.K8S_ONLINE_ENDPOINT)
        online_endpoint_dict = online_endpoint._to_dict()
        assert online_endpoint_dict["name"] == online_endpoint.name
        assert online_endpoint_dict["tags"] == online_endpoint.tags
        assert online_endpoint_dict["identity"]["type"] == online_endpoint.identity.type
        assert online_endpoint_dict["traffic"] == online_endpoint.traffic
        assert online_endpoint_dict["compute"] == "azureml:inferencecompute"

    def test_dump(self) -> None:
        online_endpoint = load_online_endpoint(TestKubernetesOnlineEndopint.K8S_ONLINE_ENDPOINT)
        online_endpoint_dict = online_endpoint.dump()
        assert online_endpoint_dict["name"] == online_endpoint.name
        assert online_endpoint_dict["tags"] == online_endpoint.tags
        assert online_endpoint_dict["identity"]["type"] == online_endpoint.identity.type
        assert online_endpoint_dict["traffic"] == online_endpoint.traffic
        assert online_endpoint_dict["compute"] == "azureml:inferencecompute"


class TestManagedOnlineEndpoint:
    ONLINE_ENDPOINT = "tests/test_configs/endpoints/online/online_endpoint_create_mir_private.yml"
    BATCH_ENDPOINT_WITH_BLUE = "tests/test_configs/endpoints/batch/batch_endpoint.yaml"

    def test_merge_with(self) -> None:
        online_endpoint = load_online_endpoint(TestManagedOnlineEndpoint.ONLINE_ENDPOINT)
        other_online_endpoint = copy.deepcopy(online_endpoint)
        other_online_endpoint.tags = {"tag3": "value3"}
        other_online_endpoint.traffic = {"blue": 90, "green": 10}
        other_online_endpoint.description = "new description"
        other_online_endpoint.mirror_traffic = {"blue": 30}
        other_online_endpoint.auth_mode = "aml_token"
        other_online_endpoint.defaults = {"deployment_name": "blue"}

        online_endpoint._merge_with(other_online_endpoint)

        assert isinstance(online_endpoint, ManagedOnlineEndpoint)
        assert online_endpoint.tags == {"dummy": "dummy", "endpointkey1": "newval1", "tag3": "value3"}
        assert online_endpoint.description == "new description"
        assert online_endpoint.traffic == {"blue": 90, "green": 10}
        assert online_endpoint.mirror_traffic == {"blue": 30}
        assert online_endpoint.auth_mode == "aml_token"
        assert online_endpoint.defaults == {"deployment_name": "blue"}

    def test_merge_with_throws_exception_when_name_masmatch(self) -> None:
        online_endpoint = load_online_endpoint(TestManagedOnlineEndpoint.ONLINE_ENDPOINT)
        other_online_endpoint = copy.deepcopy(online_endpoint)
        other_online_endpoint.name = "new_name"

        with pytest.raises(ValidationException) as ex:
            online_endpoint._merge_with(other_online_endpoint)
        assert (
            ex.value.exc_msg
            == "The endpoint name: mire2etest and new_name are not matched when merging., NoneType: None"
        )

    def test_to_dict(self) -> None:
        online_endpoint = load_online_endpoint(TestManagedOnlineEndpoint.ONLINE_ENDPOINT)
        online_endpoint_dict = online_endpoint._to_dict()
        assert online_endpoint_dict["name"] == online_endpoint.name
        assert online_endpoint_dict["tags"] == online_endpoint.tags
        assert online_endpoint_dict["identity"]["type"] == online_endpoint.identity.type
        assert online_endpoint_dict["traffic"] == online_endpoint.traffic

    def test_dump(self) -> None:
        online_endpoint = load_online_endpoint(TestManagedOnlineEndpoint.ONLINE_ENDPOINT)
        online_endpoint_dict = online_endpoint.dump()
        assert online_endpoint_dict["name"] == online_endpoint.name
        assert online_endpoint_dict["tags"] == online_endpoint.tags
        assert online_endpoint_dict["identity"]["type"] == online_endpoint.identity.type
        assert online_endpoint_dict["traffic"] == online_endpoint.traffic

    @pytest.mark.skipif(
        condition=sys.version_info >= (3, 13), reason="historical implementation doesn't support Python 3.13+"
    )
    def test_equality(self) -> None:
        online_endpoint = load_online_endpoint(TestManagedOnlineEndpoint.ONLINE_ENDPOINT)
        batch_online_endpoint = load_batch_endpoint(TestManagedOnlineEndpoint.BATCH_ENDPOINT_WITH_BLUE)

        assert online_endpoint.__eq__(None)
        assert online_endpoint.__eq__(batch_online_endpoint)

        other_online_endpoint = copy.deepcopy(online_endpoint)
        assert online_endpoint == other_online_endpoint
        assert not online_endpoint != other_online_endpoint

        other_online_endpoint.auth_mode = None
        assert not online_endpoint == other_online_endpoint
        assert online_endpoint != other_online_endpoint

        other_online_endpoint.auth_mode = online_endpoint.auth_mode
        other_online_endpoint.name = "new_name"
        assert not online_endpoint == other_online_endpoint

        online_endpoint.name = None
        assert not online_endpoint == other_online_endpoint

        other_online_endpoint.name = None
        assert online_endpoint == other_online_endpoint


class TestEndpointAuthKeys:
    def test_to_rest_object(self) -> None:
        auth_keys = EndpointAuthKeys(primary_key="primary_key", secondary_key="secondary_key")
        auth_keys_rest = auth_keys._to_rest_object()
        assert auth_keys_rest.primary_key == "primary_key"
        assert auth_keys_rest.secondary_key == "secondary_key"

    def test_from_rest_object(self) -> None:
        rest_auth_keys = RestEndpointAuthKeys(primary_key="primary_key", secondary_key="secondary_key")
        auth_keys = EndpointAuthKeys._from_rest_object(rest_auth_keys)
        assert auth_keys.primary_key == "primary_key"
        assert auth_keys.secondary_key == "secondary_key"


class TestEndpointAuthToken:
    def test_to_rest_object(self) -> None:
        auth_token = (
            EndpointAuthToken(
                access_token="token",
                expiry_time_utc="2021-10-01T00:00:00Z",
                refresh_after_time_utc="2021-10-01T00:00:00Z",
                token_type="Bearer",
            ),
        )
        auth_token_rest = auth_token[0]._to_rest_object()
        assert auth_token_rest.access_token == "token"
        assert auth_token_rest.expiry_time_utc == "2021-10-01T00:00:00Z"
        assert auth_token_rest.refresh_after_time_utc == "2021-10-01T00:00:00Z"
        assert auth_token_rest.token_type == "Bearer"

    def test_from_rest_object(self) -> None:
        rest_auth_token = RestEndpointAuthToken(
            access_token="token",
            expiry_time_utc="2021-10-01T00:00:00Z",
            refresh_after_time_utc="2021-10-01T00:00:00Z",
            token_type="Bearer",
        )
        auth_token = EndpointAuthToken._from_rest_object(rest_auth_token)
        assert auth_token.access_token == "token"
        assert auth_token.expiry_time_utc == "2021-10-01T00:00:00Z"
        assert auth_token.refresh_after_time_utc == "2021-10-01T00:00:00Z"
        assert auth_token.token_type == "Bearer"
