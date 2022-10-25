# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from azure.ai.ml import MLClient, load_registry
from azure.ai.ml.constants._common import LROConfigurations
from azure.core.paging import ItemPaged
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.ai.ml._restclient.v2022_10_01_preview.operations._registries_operations import RegistriesOperations 
import time

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
        rest_registry = crud_registry_client.registries._operation.get(resource_group_name=crud_registry_client.resource_group_name, registry_name=reg_name)
        assert rest_registry
        # don't do a standard dictionary equality check to avoid being surprised by auto-set tags
        assert rest_registry.tags["one"] == "two"
        assert rest_registry.tags["three"] == "five"
        assert rest_registry.properties.managed_resource_group_tags["one"] == "two"
        assert rest_registry.properties.managed_resource_group_tags["three"] == "five"

        registry = crud_registry_client.registries.delete(name=reg_name)
        assert registry is None
        # give the delete operation time to fully take place in the backend
        # before testing that the registry is gone with another get command
        if is_live():
            time.sleep(120)
        try:
            crud_registry_client.registries.get(name=reg_name)
            # The above line should fail with a ResourceNotFoundError
            assert False
        except ResourceNotFoundError:
            assert True