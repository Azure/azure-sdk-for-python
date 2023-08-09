from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient, load_compute
from azure.ai.ml.entities._compute.aml_compute import AmlCompute
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.mlc
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.core_sdk_test
class TestCompute(AzureRecordedTestCase):
    def test_aml_compute_create_and_delete(self, client: MLClient, rand_compute_name: Callable[[str], str]) -> None:
        compute_name = rand_compute_name("compute_name")
        params_override = [{"name": compute_name}]
        compute = load_compute(
            source="./tests/test_configs/compute/compute-aml-no-identity.yaml", params_override=params_override
        )
        compute_resource_poller = client.compute.begin_create_or_update(compute)
        assert isinstance(compute_resource_poller, LROPoller)

        compute_resource = compute_resource_poller.result()

        assert compute_resource.name == compute_name
        compute_resource_get: AmlCompute = client.compute.get(name=compute_name)
        assert compute_resource_get.name == compute_name
        assert compute_resource_get.tier == "dedicated"
        assert compute_resource_get.location == compute.location

        compute_resource_get.idle_time_before_scale_down = 200
        compute_update_poller = client.compute.begin_update(compute_resource_get)
        assert isinstance(compute_update_poller, LROPoller)
        compute_update_poller.result()

        compute_resource_get: AmlCompute = client.compute.get(name=compute_name)
        assert compute_resource_get.name == compute_name
        assert compute_resource_get.tier == "dedicated"
        assert compute_resource_get.idle_time_before_scale_down == 200

        outcome = client.compute.begin_delete(name=compute_name)
        # the compute is getting deleted , but not waiting on the poller! so immediately returning
        # so this is a preferred approach to assert
        assert isinstance(outcome, LROPoller)

    @pytest.mark.skip(reason="not enough capacity")
    def test_compute_instance_create_and_delete(
        self, client: MLClient, rand_compute_name: Callable[[str], str]
    ) -> None:
        compute_name = rand_compute_name("compute_name")
        params_override = [{"name": compute_name}]
        compute = load_compute(
            source="./tests/test_configs/compute/compute-ci.yaml",
            params_override=params_override,
        )
        compute_resource_poller = client.compute.begin_create_or_update(compute=compute)
        assert isinstance(compute_resource_poller, LROPoller)

        compute_resource = compute_resource_poller.result()
        assert compute_resource.name == compute_name
        compute_resource_list = client.compute.list()
        assert isinstance(compute_resource_list, ItemPaged)
        compute_resource_get = client.compute.get(name=compute_name)
        assert compute_resource_get.name == compute_name
        assert compute_resource_get.identity.type == "system_assigned"
        outcome = client.compute.begin_delete(name=compute_name)
        # the compute is getting deleted , but not waiting on the poller! so immediately returning
        # so this is a preferred approach to assert
        assert isinstance(outcome, LROPoller)

    @pytest.mark.skipif(
        condition=not is_live(),
        reason=(
            "Test takes 5 minutes in automation. "
            "Already have unit tests verifying correct _restclient method is called. "
            "Can be validated in live build only."
        ),
    )
    def test_compute_instance_stop_start_restart(
        self, client: MLClient, rand_compute_name: Callable[[str], str]
    ) -> None:
        compute_name = rand_compute_name("compute_name")
        params_override = [{"name": compute_name}]
        compute = load_compute(
            source="./tests/test_configs/compute/compute-ci.yaml",
            params_override=params_override,
        )
        # CI Creation
        compute_resource_poller = client.compute.begin_create_or_update(compute=compute)
        assert isinstance(compute_resource_poller, LROPoller)
        compute_resource = compute_resource_poller.result()
        assert compute_resource.name == compute_name
        assert compute_resource.state == "Running"

        # CI Stop
        compute_resource_poller = client.compute.begin_stop(name=compute_name)
        assert isinstance(compute_resource_poller, LROPoller)
        assert compute_resource_poller.result() is None
        compute_resource_get = client.compute.get(name=compute_name)
        assert compute_resource_get.state == "Stopped"

        # CI Start
        compute_resource_poller = client.compute.begin_start(name=compute_name)
        assert isinstance(compute_resource_poller, LROPoller)
        assert compute_resource_poller.result() is None
        compute_resource_get = client.compute.get(name=compute_name)
        assert compute_resource_get.state == "Running"

        # CI Delete
        outcome = client.compute.begin_delete(name=compute_name)
        # the compute is getting deleted , but not waiting on the poller! so immediately returning
        # so this is a preferred approach to assert
        assert isinstance(outcome, LROPoller)
