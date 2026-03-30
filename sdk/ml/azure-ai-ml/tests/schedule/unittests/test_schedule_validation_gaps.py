from typing import Callable
import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities._monitoring.target import MonitoringTarget
from azure.ai.ml.constants._common import ARM_ID_PREFIX, NAMED_RESOURCE_ID_FORMAT_WITH_PARENT, AZUREML_RESOURCE_PROVIDER, AzureMLResourceType
from azure.ai.ml._utils.utils import snake_to_camel


@pytest.mark.unittest
class TestScheduleOperationsInitGaps:
    def test_schedule_operations_initialized_via_mlclient(self, client: MLClient) -> None:
        # Access the ScheduleOperations instance created on MLClient construction to exercise its __init__
        sched_ops = client.schedules
        # internal attributes set in __init__ should exist
        assert hasattr(sched_ops, "service_client")
        assert hasattr(sched_ops, "schedule_trigger_service_client")
        assert hasattr(sched_ops, "_all_operations")
        assert hasattr(sched_ops, "_stream_logs_until_completion")
        # default container value set in __init__
        assert getattr(sched_ops, "_container") == "azureml"


@pytest.mark.unittest
class TestScheduleOperationsGapsGenerated:
    def test_process_and_get_endpoint_deployment_names_from_id_named_and_arm(self, client: MLClient) -> None:
        ops = client.schedules
        # Case 1: named format "endpoint:deployment" -> should be expanded to full ARM id and return names
        target_named = MonitoringTarget(endpoint_deployment_id="myendpoint:mydeployment")
        endpoint_name, deployment_name = ops._process_and_get_endpoint_deployment_names_from_id(target_named)
        assert endpoint_name == "myendpoint"
        assert deployment_name == "mydeployment"
        # After processing, endpoint_deployment_id should be converted to a full ARM formatted id
        assert "/onlineEndpoints/" in target_named.endpoint_deployment_id
        assert "/deployments/" in target_named.endpoint_deployment_id

        # Case 2: full ARM id (with azureml: prefix) -> should parse without modification other than stripping prefix
        # Build a full ARM id referencing an endpoint and deployment
        subscription = ops._subscription_id
        rg = ops._resource_group_name
        ws = ops._workspace_name
        full_arm = (
            f"/subscriptions/{subscription}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices"
            f"/workspaces/{ws}/onlineEndpoints/endpointFoo/deployments/deployBar"
        )
        target_arm = MonitoringTarget(endpoint_deployment_id=ARM_ID_PREFIX + full_arm)
        endpoint_name2, deployment_name2 = ops._process_and_get_endpoint_deployment_names_from_id(target_arm)
        assert endpoint_name2 == "endpointFoo"
        assert deployment_name2 == "deployBar"
        # ensure stored id was stripped of the 'azureml:' prefix by the method
        assert target_arm.endpoint_deployment_id.startswith("/subscriptions/")


@pytest.mark.unittest
class TestScheduleOperationsGapsAdditional:
    def test_process_and_get_endpoint_deployment_names_from_id_named(self, client: MLClient) -> None:
        # Provide a named endpoint:deployment string and ensure it is converted to a full ARM id
        target = MonitoringTarget(endpoint_deployment_id="myendpoint:mydeployment")
        endpoint_name, deployment_name = client.schedules._process_and_get_endpoint_deployment_names_from_id(target)
        assert endpoint_name == "myendpoint"
        assert deployment_name == "mydeployment"
        expected = NAMED_RESOURCE_ID_FORMAT_WITH_PARENT.format(
            client.schedules._subscription_id,
            client.schedules._resource_group_name,
            AZUREML_RESOURCE_PROVIDER,
            client.schedules._workspace_name,
            snake_to_camel(AzureMLResourceType.ONLINE_ENDPOINT),
            "myendpoint",
            AzureMLResourceType.DEPLOYMENT,
            "mydeployment",
        )
        assert target.endpoint_deployment_id == expected

    def test_process_and_get_endpoint_deployment_names_from_id_arm(self, client: MLClient) -> None:
        # Provide a full ARM id and ensure names are extracted without modification
        ep = "ep1"
        dep = "dep1"
        arm = NAMED_RESOURCE_ID_FORMAT_WITH_PARENT.format(
            client.schedules._subscription_id,
            client.schedules._resource_group_name,
            AZUREML_RESOURCE_PROVIDER,
            client.schedules._workspace_name,
            snake_to_camel(AzureMLResourceType.ONLINE_ENDPOINT),
            ep,
            AzureMLResourceType.DEPLOYMENT,
            dep,
        )
        target = MonitoringTarget(endpoint_deployment_id=arm)
        endpoint_name, deployment_name = client.schedules._process_and_get_endpoint_deployment_names_from_id(target)
        assert endpoint_name == ep
        assert deployment_name == dep
        # ARM id should remain unchanged
        assert target.endpoint_deployment_id == arm


# Generated tests merged from batch 1 (renamed class to avoid duplicate existing class name)
@pytest.mark.unittest
class TestScheduleOperationsGapsExtra:
    def test_process_endpoint_deployment_arm_id(self, client: MLClient) -> None:
        # Full ARM id should be parsed by AMLNamedArmId path in _process_and_get_endpoint_deployment_names_from_id
        arm_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg"
            "/providers/Microsoft.MachineLearningServices/workspaces/ws"
            "/onlineEndpoints/endpointName/deployments/deploymentName"
        )
        target = MonitoringTarget(endpoint_deployment_id=arm_id)
        endpoint_name, deployment_name = client.schedules._process_and_get_endpoint_deployment_names_from_id(
            target
        )
        assert endpoint_name == "endpointName"
        assert deployment_name == "deploymentName"
        # ensure the target's endpoint_deployment_id remains a valid ARM id (not converted to named format)
        assert target.endpoint_deployment_id is not None and "/onlineEndpoints/" in target.endpoint_deployment_id

    def test_process_endpoint_deployment_arm_id_with_azureml_prefix(self, client: MLClient) -> None:
        # When prefixed with ARM_ID_PREFIX (azureml:), the prefix should be removed and ARM id parsed
        raw_arm = (
            "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg2"
            "/providers/Microsoft.MachineLearningServices/workspaces/ws2"
            "/onlineEndpoints/myEndpoint/deployments/myDeployment"
        )
        prefixed = f"azureml:{raw_arm}"
        target = MonitoringTarget(endpoint_deployment_id=prefixed)
        endpoint_name, deployment_name = client.schedules._process_and_get_endpoint_deployment_names_from_id(
            target
        )
        assert endpoint_name == "myEndpoint"
        assert deployment_name == "myDeployment"
        # after processing the azureml: prefix should be stripped from the stored id
        assert target.endpoint_deployment_id == raw_arm
