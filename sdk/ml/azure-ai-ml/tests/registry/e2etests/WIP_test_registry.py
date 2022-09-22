# # ---------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # ---------------------------------------------------------

# import pytest
# from tests.conftest import crud_registry_client

# from azure.ai.ml import MLClient
# from azure.ai.ml.entities._registry.registry import Registry
# from azure.core.paging import ItemPaged


# @pytest.mark.e2etest
# @pytest.mark.mlc
# class TestRegistry:
#     # Need to implement more verbs for this to be functional - testing on hardcoded registry within pipeline causes authorization errors
#     # However this test passed locally
#     def WIP_test_registry_list_and_get(
#         self, crud_registry_client: MLClient, randstr: Callable[[], str], location: str
#     ) -> None:
#         reg_name = "TestRegistryOperations"

#         registry = crud_registry_client.registries.get(reg_name)
#         assert registry.name == reg_name

#         registry_list = crud_registry_client.registries.list()
#         assert isinstance(registry_list, ItemPaged)
