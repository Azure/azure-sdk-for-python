# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from urllib.parse import parse_qs, urlsplit

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import ResourceModifiedError
from azure.core.rest import HttpResponse
from azure.mgmt.batch import BatchManagementClient, models
from azure.mgmt.batch.aio import BatchManagementClient as AsyncBatchManagementClient


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers():
    """These mocked unit tests do not send traffic or need the test proxy."""
    yield


@pytest.fixture
def pool_with_new_features():
    return models.Pool(
        properties=models.PoolProperties(
            vm_size="Mix",
            vm_sku_profile=models.VirtualMachineSkuProfile(
                vm_sizes=[
                    models.VirtualMachineSkuProfileVmSize(name="Standard_D8s_v5", rank=0),
                    models.VirtualMachineSkuProfileVmSize(name="Standard_D8as_v5", rank=1),
                ],
                allocation_strategy=models.VirtualMachineSkuAllocationStrategy.PRIORITIZED,
            ),
            deployment_configuration=models.DeploymentConfiguration(
                virtual_machine_configuration=models.VirtualMachineConfiguration(
                    image_reference=models.ImageReference(
                        publisher="Canonical", offer="ubuntu-24_04-lts", sku="server", version="latest"
                    ),
                    node_agent_sku_id="batch.node.ubuntu 24.04",
                    hardware_profile=models.HardwareProfile(
                        vm_size_properties=models.VmSizeProperties(v_cpus_available=4, v_cpus_per_core=1)
                    ),
                    placement=models.Placement(zone_placement_policy=models.ZonePlacementPolicyType.AUTO),
                    resiliency_policy=models.ResiliencyPolicy(
                        zone_allocation_policy=models.ZoneAllocationPolicy(
                            max_zone_count=3,
                            max_instance_percent_per_zone_policy=models.MaxInstancePercentPerZonePolicy(
                                enabled=True, value=50
                            ),
                        )
                    ),
                )
            ),
        )
    )


@pytest.fixture
def partial_pool_patch():
    return models.PoolPatch(
        properties=models.PoolPatchProperties(
            deployment_configuration=models.DeploymentConfigurationPatch(
                virtual_machine_configuration=models.VirtualMachineConfigurationPatch(
                    image_reference=models.ImageReference(
                        publisher="Canonical", offer="ubuntu-24_04-lts", sku="server", version="latest"
                    ),
                    node_agent_sku_id="batch.node.ubuntu 24.04",
                    placement=models.PlacementPatch(zone_placement_policy=models.ZonePlacementPolicyType.AUTO),
                    resiliency_policy=models.ResiliencyPolicyPatch(
                        zone_allocation_policy=models.ZoneAllocationPolicyPatch(
                            max_instance_percent_per_zone_policy=models.MaxInstancePercentPerZonePolicyPatch(
                                enabled=False
                            )
                        )
                    ),
                )
            )
        )
    )


class TestBatchPoolModels:
    def test_removed_authentication_mode(self):
        assert not hasattr(models.AuthenticationMode, "TASK_AUTHENTICATION_TOKEN")
        with pytest.raises(ValueError):
            models.AuthenticationMode("TaskAuthenticationToken")
        assert {mode.value for mode in models.AuthenticationMode} == {"SharedKey", "AAD"}

    @pytest.mark.parametrize("option", ["Requeue", "Terminate", "TaskCompletion"])
    def test_requested_deallocation_options(self, option):
        settings = models.FixedScaleSettings(
            target_dedicated_nodes=0,
            node_deallocation_option=models.RequestedComputeNodeDeallocationOption(option),
        )
        assert settings.as_dict(exclude_readonly=True) == {
            "targetDedicatedNodes": 0,
            "nodeDeallocationOption": option,
        }

    def test_retained_data_is_response_only_enum_value(self):
        assert not hasattr(models.RequestedComputeNodeDeallocationOption, "RETAINED_DATA")
        with pytest.raises(ValueError):
            models.RequestedComputeNodeDeallocationOption("RetainedData")
        status = models.ResizeOperationStatus({"nodeDeallocationOption": "RetainedData"})
        assert status.node_deallocation_option == models.ComputeNodeDeallocationOption.RETAINED_DATA

    @pytest.mark.parametrize("strategy", ["LowestPrice", "CapacityOptimized", "Prioritized"])
    def test_vm_sku_allocation_strategies(self, strategy):
        rank = 0 if strategy == "Prioritized" else None
        profile = models.VirtualMachineSkuProfile(
            vm_sizes=[models.VirtualMachineSkuProfileVmSize(name="Standard_D8s_v5", rank=rank)],
            allocation_strategy=models.VirtualMachineSkuAllocationStrategy(strategy),
        )
        expected_size = {"name": "Standard_D8s_v5"}
        if rank is not None:
            expected_size["rank"] = rank
        assert profile.as_dict() == {"vmSizes": [expected_size], "allocationStrategy": strategy}
        restored = models.VirtualMachineSkuProfile(profile.as_dict())
        assert isinstance(restored.vm_sizes[0], models.VirtualMachineSkuProfileVmSize)
        assert restored.vm_sizes[0].rank == rank
        assert restored.allocation_strategy == strategy

    def test_new_pool_features_serialization(self, pool_with_new_features):
        properties = pool_with_new_features.as_dict(exclude_readonly=True)["properties"]
        assert properties["vmSize"] == "Mix"
        assert properties["vmSkuProfile"] == {
            "vmSizes": [
                {"name": "Standard_D8s_v5", "rank": 0},
                {"name": "Standard_D8as_v5", "rank": 1},
            ],
            "allocationStrategy": "Prioritized",
        }
        vm = properties["deploymentConfiguration"]["virtualMachineConfiguration"]
        assert vm["hardwareProfile"] == {"vmSizeProperties": {"vCPUsAvailable": 4, "vCPUsPerCore": 1}}
        assert vm["placement"] == {"zonePlacementPolicy": "Auto"}
        assert vm["resiliencyPolicy"] == {
            "zoneAllocationPolicy": {
                "maxZoneCount": 3,
                "maxInstancePercentPerZonePolicy": {"enabled": True, "value": 50},
            }
        }

    def test_new_pool_features_deserialization(self, pool_with_new_features):
        pool = models.Pool(pool_with_new_features.as_dict())
        assert isinstance(pool.properties.vm_sku_profile, models.VirtualMachineSkuProfile)
        assert pool.properties.vm_sku_profile.vm_sizes[0].rank == 0
        vm = pool.properties.deployment_configuration.virtual_machine_configuration
        assert isinstance(vm.hardware_profile, models.HardwareProfile)
        assert isinstance(vm.hardware_profile.vm_size_properties, models.VmSizeProperties)
        assert vm.hardware_profile.vm_size_properties.v_cpus_available == 4
        assert vm.hardware_profile.vm_size_properties.v_cpus_per_core == 1
        assert isinstance(vm.placement, models.Placement)
        assert vm.placement.zone_placement_policy == models.ZonePlacementPolicyType.AUTO
        assert isinstance(vm.resiliency_policy, models.ResiliencyPolicy)
        policy = vm.resiliency_policy.zone_allocation_policy
        assert isinstance(policy, models.ZoneAllocationPolicy)
        assert policy.max_zone_count == 3
        assert isinstance(policy.max_instance_percent_per_zone_policy, models.MaxInstancePercentPerZonePolicy)
        assert policy.max_instance_percent_per_zone_policy.enabled is True
        assert policy.max_instance_percent_per_zone_policy.value == 50

    def test_partial_zone_patch_omits_unspecified_fields(self, partial_pool_patch):
        properties = partial_pool_patch.as_dict(exclude_readonly=True)["properties"]
        assert set(properties) == {"deploymentConfiguration"}
        vm = properties["deploymentConfiguration"]["virtualMachineConfiguration"]
        assert vm["placement"] == {"zonePlacementPolicy": "Auto"}
        assert vm["resiliencyPolicy"] == {
            "zoneAllocationPolicy": {"maxInstancePercentPerZonePolicy": {"enabled": False}}
        }
        assert "hardwareProfile" not in vm

    def test_empty_patch_and_explicit_null_are_distinct(self):
        assert models.PoolPatch().as_dict(exclude_readonly=True) == {}
        patch = models.PoolPatch(properties=models.PoolPatchProperties({"startTask": None}))
        assert patch.as_dict(exclude_readonly=True) == {"properties": {"startTask": None}}

    def test_patch_excludes_readonly_fields(self):
        patch = models.PoolPatch(
            {
                "id": "/subscriptions/sub/resourceGroups/group/providers/Microsoft.Batch/batchAccounts/account/pools/pool",
                "etag": "old-etag",
                "systemData": {"createdBy": "example"},
                "tags": {"environment": "test"},
                "properties": {"currentDedicatedNodes": 2, "displayName": "updated"},
            }
        )
        assert patch.as_dict(exclude_readonly=True) == {
            "tags": {"environment": "test"},
            "properties": {"displayName": "updated"},
        }


class TestBatchPoolOperations:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
    @pytest.mark.parametrize("operation", ["create", "get", "update"])
    async def test_new_features_on_wire(
        self, monkeypatch, pool_with_new_features, partial_pool_patch, is_async, operation
    ):
        client_type = AsyncBatchManagementClient if is_async else BatchManagementClient
        client = client_type(credential=Mock(), subscription_id="00000000-0000-0000-0000-000000000000")
        response = Mock(spec=HttpResponse)
        response.status_code = 200
        response.headers = {"ETag": "new-etag"}
        response.json.return_value = pool_with_new_features.as_dict()
        run = (AsyncMock if is_async else Mock)(return_value=SimpleNamespace(http_response=response))
        monkeypatch.setattr(client._client._pipeline, "run", run)
        try:
            parameters = []
            if operation != "get":
                parameters.append(partial_pool_patch if operation == "update" else pool_with_new_features)
            result = getattr(client.pool, operation)("group", "account", "pool", *parameters)
            if is_async:
                result = await result
            run.assert_called_once()
            request = run.call_args.args[0]
            assert request.method == {"create": "PUT", "get": "GET", "update": "PATCH"}[operation]
            url = urlsplit(request.url)
            assert url.path.endswith("/resourceGroups/group/providers/Microsoft.Batch/batchAccounts/account/pools/pool")
            assert parse_qs(url.query)["api-version"] == ["2026-10-01"]
            if parameters:
                assert request.headers["Content-Type"] == "application/json"
                assert json.loads(request.content) == parameters[0].as_dict(exclude_readonly=True)
            assert isinstance(result, models.Pool)
            assert isinstance(result.properties.vm_sku_profile, models.VirtualMachineSkuProfile)
            assert result.properties.vm_sku_profile.vm_sizes[0].rank == 0
            vm = result.properties.deployment_configuration.virtual_machine_configuration
            assert vm.hardware_profile.vm_size_properties.v_cpus_per_core == 1
            assert vm.placement.zone_placement_policy == models.ZonePlacementPolicyType.AUTO
            assert vm.resiliency_policy.zone_allocation_policy.max_instance_percent_per_zone_policy.value == 50
        finally:
            if is_async:
                await client.close()
            else:
                client.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
    async def test_pool_patch_preserves_etag_conflict(self, monkeypatch, partial_pool_patch, is_async):
        client_type = AsyncBatchManagementClient if is_async else BatchManagementClient
        client = client_type(credential=Mock(), subscription_id="00000000-0000-0000-0000-000000000000")
        response = Mock(spec=HttpResponse)
        response.status_code = 412
        response.reason = "Precondition Failed"
        response.headers = {"Content-Type": "application/json"}
        response.json.return_value = {"error": {"code": "ConditionNotMet", "message": "The pool was modified."}}
        run = (AsyncMock if is_async else Mock)(return_value=SimpleNamespace(http_response=response))
        monkeypatch.setattr(client._client._pipeline, "run", run)
        try:
            with pytest.raises(ResourceModifiedError):
                result = client.pool.update(
                    "group",
                    "account",
                    "pool",
                    partial_pool_patch,
                    etag="old-etag",
                    match_condition=MatchConditions.IfNotModified,
                )
                if is_async:
                    await result
            run.assert_called_once()
            assert run.call_args.args[0].headers["If-Match"] == '"old-etag"'
        finally:
            if is_async:
                await client.close()
            else:
                client.close()
