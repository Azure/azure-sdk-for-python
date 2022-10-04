# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from azure.ai.ml import MLClient, load_registry
from azure.ai.ml.constants._common import LROConfigurations
from azure.core.paging import ItemPaged
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestRegistry(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_registry_list_and_get(
        self,
        crud_registry_client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        reg_name = f"e2etest{randstr('reg_name')}"
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
