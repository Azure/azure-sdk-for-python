# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_registry
from azure.ai.ml.constants._common import LROConfigurations
from azure.ai.ml.constants._registry import StorageAccountType
from azure.core.paging import ItemPaged


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.production_experiences_test
class TestRegistry(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_registry_operations(
        self,
        crud_registry_client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        # Registries cannot currently handle names with underscores,
        # so remove it from the randomly generated registry name
        # to avoid problems.
        reg_name = "".join(f"{randstr('reg_name')}".split("_"))
        params_override = [
            {
                "name": reg_name,
            }
        ]
        reg = load_registry(
            source="./tests/test_configs/registry/registry_valid_min.yaml", params_override=params_override
        )
        registry = crud_registry_client.registries.begin_create(registry=reg).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert registry.name == reg_name
        assert registry.identity.type == "SystemAssigned"

        registry_list = crud_registry_client.registries.list()
        assert isinstance(registry_list, ItemPaged)

        registry = crud_registry_client.registries.get(name=reg_name)
        assert registry.name == reg_name

        # Some values are assigned by registries, but hidden in the local representation to avoid confusing users.
        # Double check that they're set properly by examining the raw registry format.
        rest_registry = crud_registry_client.registries._operation.get(
            resource_group_name=crud_registry_client.resource_group_name, registry_name=reg_name
        )
        assert rest_registry
        # don't do a standard dictionary equality check to avoid being surprised by auto-set tags
        assert rest_registry.tags["one"] == "two"
        assert rest_registry.tags["three"] == "five"
        # TODO re-enable once managed RG tags in all regions and stable
        # assert rest_registry.properties.managed_resource_group_tags["one"] == "two"
        # assert rest_registry.properties.managed_resource_group_tags["three"] == "five"

        del_result = crud_registry_client.registries.begin_delete(name=reg_name).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert del_result is None

    def test_registry_operations_with_storage_replication(
        self,
        crud_registry_client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        # Registries cannot currently handle names with underscores,
        # so remove it from the randomly generated registry name
        # to avoid problems.
        reg_name = "".join(f"{randstr('reg_name')}".split("_"))
        params_override = [
            {
                "name": reg_name,
            }
        ]
        reg = load_registry(
            source="./tests/test_configs/registry/registry_valid_e2e_replication.yaml", params_override=params_override
        )
        registry = crud_registry_client.registries.begin_create(registry=reg).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )

        assert registry.name == reg_name
        assert registry.replication_locations[0].storage_config.replication_count == 3
        assert registry.replication_locations[0].storage_config.storage_account_hns == False
        assert registry.replication_locations[0].storage_config.storage_account_type == StorageAccountType.STANDARD_LRS

        registry_list = crud_registry_client.registries.list()
        assert isinstance(registry_list, ItemPaged)

        registry = crud_registry_client.registries.get(name=reg_name)
        assert registry.name == reg_name

        # Some values are assigned by registries, but hidden in the local representation to avoid confusing users.
        # Double check that they're set properly by examining the raw registry format.
        rest_registry = crud_registry_client.registries._operation.get(
            resource_group_name=crud_registry_client.resource_group_name, registry_name=reg_name
        )
        assert rest_registry

        # ensure that the underlying data behind the replicated storage looks reasonable.

        del_result = crud_registry_client.registries.begin_delete(name=reg_name).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert del_result is None
