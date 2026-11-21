# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import unittest
from functools import partial
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.rest import HttpResponse
from azure.batch import BatchClient, models
from azure.batch.aio import BatchClient as AsyncBatchClient


ENDPOINT = "https://account.region.batch.azure.com"
POOL_ID = "api-feature-pool"
SKU_NAMES = ("Standard_D2s_v5", "Standard_D2as_v5")


def feature_pool(strategy=None, zone_policy=False, percent_enabled=True):
    configuration = models.VirtualMachineConfiguration(
        image_reference=models.BatchVmImageReference(
            publisher="Canonical", offer="0001-com-ubuntu-server-jammy", sku="22_04-lts"
        ),
        node_agent_sku_id="batch.node.ubuntu 22.04",
    )
    if zone_policy:
        configuration.placement = models.Placement(zone_placement_policy=models.ZonePlacementPolicyType.AUTO)
        configuration.resiliency_policy = models.ResiliencyPolicy(
            zone_allocation_policy=models.ZoneAllocationPolicy(
                max_zone_count=3,
                max_instance_percent_per_zone_policy=models.MaxInstancePercentPerZonePolicy(
                    enabled=percent_enabled, value=50
                ),
            )
        )
        configuration.hardware_profile = models.HardwareProfile(
            vm_size_properties=models.VMSizeProperties(v_cpus_available=2, v_cpus_per_core=1)
        )
    profile = None
    if strategy is not None:
        profile = models.VirtualMachineSkuProfile(
            vm_sizes=[
                models.VirtualMachineSkuProfileVmSize(
                    name=name,
                    rank=index if strategy == models.VirtualMachineSkuAllocationStrategy.PRIORITIZED else None,
                )
                for index, name in enumerate(SKU_NAMES)
            ],
            allocation_strategy=strategy,
        )
    return models.BatchPoolCreateOptions(
        id=POOL_ID,
        vm_size="Mix" if profile is not None else SKU_NAMES[0],
        vm_sku_profile=profile,
        target_dedicated_nodes=0,
        target_low_priority_nodes=0,
        virtual_machine_configuration=configuration,
    )


def expected_pool_payload(strategy=None, zone_policy=False, percent_enabled=True):
    payload = {
        "id": POOL_ID,
        "vmSize": "Mix" if strategy is not None else SKU_NAMES[0],
        "targetDedicatedNodes": 0,
        "targetLowPriorityNodes": 0,
        "virtualMachineConfiguration": {
            "imageReference": {
                "publisher": "Canonical",
                "offer": "0001-com-ubuntu-server-jammy",
                "sku": "22_04-lts",
            },
            "nodeAgentSKUId": "batch.node.ubuntu 22.04",
        },
    }
    if strategy is not None:
        sizes = [{"name": name} for name in SKU_NAMES]
        if strategy == models.VirtualMachineSkuAllocationStrategy.PRIORITIZED:
            for index, size in enumerate(sizes):
                size["rank"] = index
        payload["vmSkuProfile"] = {"vmSizes": sizes, "allocationStrategy": strategy.value}
    if zone_policy:
        payload["virtualMachineConfiguration"].update(
            {
                "placement": {"zonePlacementPolicy": "Auto"},
                "resiliencyPolicy": {
                    "zoneAllocationPolicy": {
                        "maxZoneCount": 3,
                        "maxInstancePercentPerZonePolicy": {"enabled": percent_enabled, "value": 50},
                    }
                },
                "hardwareProfile": {"vmSizeProperties": {"vCPUsAvailable": 2, "vCPUsPerCore": 1}},
            }
        )
    return payload


def assert_feature_pool(pool, strategy=None, zone_policy=False, percent_enabled=True):
    assert isinstance(pool, models.BatchPool)
    assert pool.id == POOL_ID
    assert pool.vm_size.lower() == ("Mix" if strategy is not None else SKU_NAMES[0]).lower()
    assert pool.target_dedicated_nodes == 0
    assert pool.target_low_priority_nodes == 0
    if strategy is not None:
        assert isinstance(pool.vm_sku_profile, models.VirtualMachineSkuProfile)
        assert pool.vm_sku_profile.allocation_strategy == strategy
        assert [size.name for size in pool.vm_sku_profile.vm_sizes] == list(SKU_NAMES)
        expected_ranks = [0, 1] if strategy == models.VirtualMachineSkuAllocationStrategy.PRIORITIZED else [None, None]
        assert [size.rank for size in pool.vm_sku_profile.vm_sizes] == expected_ranks
        for size in pool.vm_sku_profile.vm_sizes:
            assert isinstance(size, models.VirtualMachineSkuProfileVmSize)
    if zone_policy:
        configuration = pool.virtual_machine_configuration
        assert isinstance(configuration.placement, models.Placement)
        assert configuration.placement.zone_placement_policy == models.ZonePlacementPolicyType.AUTO
        assert isinstance(configuration.resiliency_policy, models.ResiliencyPolicy)
        policy = configuration.resiliency_policy.zone_allocation_policy
        assert isinstance(policy, models.ZoneAllocationPolicy)
        assert policy.max_zone_count == 3
        assert isinstance(policy.max_instance_percent_per_zone_policy, models.MaxInstancePercentPerZonePolicy)
        assert policy.max_instance_percent_per_zone_policy.enabled == percent_enabled
        assert policy.max_instance_percent_per_zone_policy.value == 50
        assert isinstance(configuration.hardware_profile, models.HardwareProfile)
        assert isinstance(configuration.hardware_profile.vm_size_properties, models.VMSizeProperties)
        assert configuration.hardware_profile.vm_size_properties.v_cpus_available == 2
        assert configuration.hardware_profile.vm_size_properties.v_cpus_per_core == 1


def api_response(request, body=None, status=201):
    response = Mock(spec=HttpResponse)
    response.request = request
    response.status_code = status
    response.headers = {"content-type": "application/json"} if body is not None else {}
    response.content_type = "application/json" if body is not None else ""
    response.content = json.dumps(body).encode() if body is not None else b""
    response.text.return_value = response.content.decode()
    response.json.return_value = body
    return response


def pool_transport_response(request, expected, **_kwargs):
    if request.method == "POST":
        assert request.url == ENDPOINT + "/pools?api-version=2026-10-01"
        assert json.loads(request.content) == expected
        return api_response(request)
    assert request.method == "GET"
    assert request.url == ENDPOINT + "/pools/" + POOL_ID + "?api-version=2026-10-01"
    return api_response(request, body=expected, status=200)


def task_completion_cases():
    return (
        (
            "begin_deallocate_node", ("pool", "node"),
            models.BatchNodeDeallocateOptions(node_deallocate_option=models.BatchNodeDeallocateOption.TASK_COMPLETION),
            {"nodeDeallocateOption": "taskcompletion"},
        ),
        (
            "begin_reboot_node", ("pool", "node"),
            models.BatchNodeRebootOptions(node_reboot_kind=models.BatchNodeRebootKind.TASK_COMPLETION),
            {"nodeRebootOption": "taskcompletion"},
        ),
        (
            "begin_reimage_node", ("pool", "node"),
            models.BatchNodeReimageOptions(node_reimage_option=models.BatchNodeReimageOption.TASK_COMPLETION),
            {"nodeReimageOption": "taskcompletion"},
        ),
        (
            "begin_remove_nodes", ("pool",),
            models.BatchNodeRemoveOptions(
                node_ids=["node"], node_deallocation_option=models.BatchNodeDeallocationOption.TASK_COMPLETION
            ),
            {"nodeList": ["node"], "nodeDeallocationOption": "taskcompletion"},
        ),
    )


class TestPoolApi(unittest.TestCase):
    def test_create_get_feature_pool_payloads(self):
        cases = [(strategy, False, True) for strategy in models.VirtualMachineSkuAllocationStrategy]
        cases += [(None, True, enabled) for enabled in (True, False)]
        cases.append((models.VirtualMachineSkuAllocationStrategy.PRIORITIZED, True, True))
        for strategy, zone_policy, enabled in cases:
            with self.subTest(strategy=strategy, zone_policy=zone_policy, enabled=enabled):
                expected = expected_pool_payload(strategy, zone_policy, enabled)
                transport = MagicMock()
                transport.send.side_effect = partial(pool_transport_response, expected=expected)
                with BatchClient(
                    ENDPOINT, AzureNamedKeyCredential("account", "ZmFrZQ=="), transport=transport
                ) as client:
                    self.assertIsNone(client.create_pool(feature_pool(strategy, zone_policy, enabled)))
                    pool = client.get_pool(POOL_ID)
                self.assertEqual(transport.send.call_count, 2)
                assert_feature_pool(pool, strategy, zone_policy, enabled)

    def test_omitted_policies_are_not_added_to_request_or_response(self):
        expected = expected_pool_payload()
        transport = MagicMock()
        transport.send.side_effect = partial(pool_transport_response, expected=expected)
        with BatchClient(ENDPOINT, AzureNamedKeyCredential("account", "ZmFrZQ=="), transport=transport) as client:
            client.create_pool(feature_pool())
            pool = client.get_pool(POOL_ID)
        self.assertIsNone(pool.vm_sku_profile)
        self.assertIsNone(pool.virtual_machine_configuration.placement)
        self.assertIsNone(pool.virtual_machine_configuration.resiliency_policy)
        self.assertIsNone(pool.virtual_machine_configuration.hardware_profile)

    def test_task_completion_option_wire_values(self):
        for name, args, options, expected in task_completion_cases():
            with self.subTest(operation=name):
                transport = MagicMock()
                transport.send.side_effect = lambda request, **_kwargs: api_response(request, status=202)
                with BatchClient(
                    ENDPOINT, AzureNamedKeyCredential("account", "ZmFrZQ=="), transport=transport
                ) as client:
                    with patch("azure.batch._operations._patch.LROPoller"):
                        getattr(client, name)(*args, options, polling_interval=0)
                request = transport.send.call_args.args[0]
                self.assertEqual(request.method, "POST")
                self.assertEqual(json.loads(request.content), expected)
                self.assertNotIn("retaineddata", request.content)


class TestAsyncPoolApi(unittest.IsolatedAsyncioTestCase):
    async def test_create_get_feature_pool_payloads(self):
        cases = [(strategy, False, True) for strategy in models.VirtualMachineSkuAllocationStrategy]
        cases += [(None, True, enabled) for enabled in (True, False)]
        cases.append((models.VirtualMachineSkuAllocationStrategy.PRIORITIZED, True, True))
        for strategy, zone_policy, enabled in cases:
            with self.subTest(strategy=strategy, zone_policy=zone_policy, enabled=enabled):
                expected = expected_pool_payload(strategy, zone_policy, enabled)
                transport = MagicMock()
                transport.send = AsyncMock(side_effect=partial(pool_transport_response, expected=expected))
                transport.close = AsyncMock()
                async with AsyncBatchClient(
                    ENDPOINT, AzureNamedKeyCredential("account", "ZmFrZQ=="), transport=transport
                ) as client:
                    self.assertIsNone(await client.create_pool(feature_pool(strategy, zone_policy, enabled)))
                    pool = await client.get_pool(POOL_ID)
                self.assertEqual(transport.send.await_count, 2)
                assert_feature_pool(pool, strategy, zone_policy, enabled)

    async def test_omitted_policies_are_not_added_to_request_or_response(self):
        expected = expected_pool_payload()
        transport = MagicMock()
        transport.send = AsyncMock(side_effect=partial(pool_transport_response, expected=expected))
        transport.close = AsyncMock()
        async with AsyncBatchClient(
            ENDPOINT, AzureNamedKeyCredential("account", "ZmFrZQ=="), transport=transport
        ) as client:
            await client.create_pool(feature_pool())
            pool = await client.get_pool(POOL_ID)
        self.assertIsNone(pool.vm_sku_profile)
        self.assertIsNone(pool.virtual_machine_configuration.placement)
        self.assertIsNone(pool.virtual_machine_configuration.resiliency_policy)
        self.assertIsNone(pool.virtual_machine_configuration.hardware_profile)

    async def test_task_completion_option_wire_values(self):
        for name, args, options, expected in task_completion_cases():
            with self.subTest(operation=name):
                transport = MagicMock()
                transport.send = AsyncMock(side_effect=lambda request, **_kwargs: api_response(request, status=202))
                transport.close = AsyncMock()
                async with AsyncBatchClient(
                    ENDPOINT, AzureNamedKeyCredential("account", "ZmFrZQ=="), transport=transport
                ) as client:
                    with patch("azure.batch.aio._operations._patch.AsyncLROPoller"):
                        await getattr(client, name)(*args, options, polling_interval=0)
                request = transport.send.call_args.args[0]
                self.assertEqual(request.method, "POST")
                self.assertEqual(json.loads(request.content), expected)
                self.assertNotIn("retaineddata", request.content)
