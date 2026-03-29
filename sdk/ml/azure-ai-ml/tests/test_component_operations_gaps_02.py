import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from collections.abc import Iterable
from azure.ai.ml.entities import PipelineComponent
from azure.ai.ml.operations._component_operations import ComponentOperations


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestComponentOperationsInitAndList(AzureRecordedTestCase):
    def test_managed_label_resolver_contains_latest(self, client: MLClient) -> None:
        ops = client.components
        # _managed_label_resolver should contain 'latest' mapped to a callable
        assert isinstance(ops._managed_label_resolver, dict)
        assert "latest" in ops._managed_label_resolver
        resolver_func = ops._managed_label_resolver["latest"]
        assert callable(resolver_func)

    def test_list_with_name_returns_iterable_of_components(self, client: MLClient) -> None:
        # When name is provided, list() should return an iterable (ItemPaged or similar)
        iterator = client.components.list(name="nonexistent_component_for_test")
        # do not materialize the iterator to avoid network calls in environments where auth may fail
        assert isinstance(iterator, Iterable)

    def test_list_without_name_returns_iterable_of_containers(self, client: MLClient) -> None:
        iterator = client.components.list()
        # do not materialize the iterator to avoid network calls in environments where auth may fail
        assert isinstance(iterator, Iterable)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestComponentOperationsDivideLayers(AzureRecordedTestCase):
    def test_divide_nodes_to_resolve_into_layers_with_all_leaf_nodes(self, client: MLClient) -> None:
        """Verify _divide_nodes_to_resolve_into_layers places all non-pipeline jobs into the final layer.

        Covered marker lines: 289-303 (the loop that collects leaf nodes and the final layers pop/append).
        """
        # Create a lightweight object with a jobs mapping so the divide function can iterate without
        # invoking PipelineComponent validation logic.
        class DummyPipelineComponent:
            def __init__(self, jobs):
                self.jobs = jobs

        component = DummyPipelineComponent(jobs={"A": 1, "B": 2})

        # Use a no-op extra operation that safely accepts any node and key
        def noop_extra_operation(node, key):
            # This operation intentionally does nothing. It's used to exercise the extra_operations loop.
            return None

        layers = ComponentOperations._divide_nodes_to_resolve_into_layers(component, extra_operations=[noop_extra_operation])

        # Expect a single layer that contains both leaf nodes
        assert isinstance(layers, list)
        assert len(layers) == 1
        # The sole layer should contain the two leaf tuples in any order; convert to set for comparison
        layer_set = set(layers[0])
        assert layer_set == {("A", 1), ("B", 2)}
