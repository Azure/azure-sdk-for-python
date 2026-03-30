import types
from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities import PipelineComponent
from azure.ai.ml.exceptions import ValidationException, ComponentException


@pytest.fixture
def randstr():
    """Generate a random string for test isolation."""
    import random, string
    def _gen(prefix=""):
        return prefix + "".join(random.choices(string.ascii_lowercase, k=8))
    return _gen


@pytest.mark.unittest
class TestComponentOperationsEarlyBranches:
    def test_get_with_both_version_and_label_raises(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """
        Covers the _get branch that raises when both version and label are provided.
        """

        name = randstr("component_name")
        with pytest.raises(ValidationException) as excinfo:
            client.components.get(name=name, version="1", label="latest")

        assert "Cannot specify both version and label." in str(excinfo.value)

    def test_list_returns_iterable_and_is_iterable(self, client: MLClient) -> None:
        """
        Covers the list() method return paths by asserting the returned object is iterable.
        This exercises both branches of list() selection logic depending on recorded test environment.
        """

        result = client.components.list()
        # Concrete assertion: object should be iterable
        assert hasattr(result, "__iter__")


@pytest.mark.unittest
class TestComponentOperationsGaps:
    def test_refine_component_plain_function_raises(self, client: MLClient) -> None:
        """Ensure passing a plain Python function (not DSL/mldesigner) into validate triggers
        the fallback ValidationException from _refine_component.
        """

        def plain_func(a, b):
            return a + b

        with pytest.raises(ValidationException) as ex:
            # trigger refinement via public validate API which calls _refine_component
            client.components.validate(plain_func, raise_on_failure=False)

        assert "Function must be a dsl or mldesigner component function" in str(ex.value)

    def test_refine_component_variable_args_raises(self, client: MLClient) -> None:
        """Create a function that simulates a DSL function (set _is_dsl_func) but uses
        *args so check_parameter_type raises a ValidationException for variable inputs.
        """

        def varargs_func(*args):
            return None

        # Mark it as a DSL function and attach minimal pipeline builder attributes expected by _refine_component
        varargs_func._is_dsl_func = True
        class _Builder:
            non_pipeline_parameter_names = []
            def build(self, user_provided_kwargs=None):
                return PipelineComponent()

        varargs_func._pipeline_builder = _Builder()
        varargs_func._job_settings = None

        with pytest.raises(ValidationException) as ex:
            client.components.validate(varargs_func, raise_on_failure=False)

        assert "Cannot register the component" in str(ex.value)

    def test_get_client_key_raises_when_no_workspace_or_registry(self, client: MLClient) -> None:
        """Temporarily clear workspace and registry names on the operations object to exercise the
        error branch in _get_client_key that raises ValueError when neither is present.
        """

        ops = client.components
        # Backup original values to restore after assertion
        # _workspace_name and _registry_name are exposed via the operation scope; modify the underlying scope
        orig_workspace = getattr(getattr(ops, "_operation_scope", None), "workspace_name", None)
        orig_registry = getattr(getattr(ops, "_operation_scope", None), "registry_name", None)

        try:
            # Set the underlying operation scope values to None to simulate missing client scope
            if hasattr(ops, "_operation_scope"):
                setattr(ops._operation_scope, "workspace_name", None)
                setattr(ops._operation_scope, "registry_name", None)
            with pytest.raises(ValueError) as ex:
                ops._get_client_key()
            assert "Either workspace name or registry name must be provided" in str(ex.value)
        finally:
            # restore
            if hasattr(ops, "_operation_scope"):
                setattr(ops._operation_scope, "workspace_name", orig_workspace)
                setattr(ops._operation_scope, "registry_name", orig_registry)

    def test_divide_nodes_to_resolve_into_layers_empty_jobs_returns_empty(self, client: MLClient) -> None:
        """Verify that _divide_nodes_to_resolve_into_layers returns an empty list when a
        PipelineComponent with no jobs is provided.
        """

        pc = PipelineComponent()
        layers = client.components._divide_nodes_to_resolve_into_layers(pc, extra_operations=[])
        assert layers == []


@pytest.mark.unittest
class TestComponentOperationsGapsGenerated:
    def test_get_client_key_raises_when_no_workspace_or_registry(self, client: MLClient) -> None:
        ops = client.components
        # preserve original values to restore after test
        orig_workspace = getattr(getattr(ops, "_operation_scope", None), "workspace_name", None)
        orig_registry = getattr(getattr(ops, "_operation_scope", None), "registry_name", None)
        try:
            if hasattr(ops, "_operation_scope"):
                setattr(ops._operation_scope, "workspace_name", None)
                setattr(ops._operation_scope, "registry_name", None)
            else:
                # fallback if operation scope is not available
                try:
                    ops._workspace_name = None
                except Exception:
                    pass
                try:
                    ops._registry_name = None
                except Exception:
                    pass
            with pytest.raises(ValueError) as excinfo:
                ops._get_client_key()
            assert "Either workspace name or registry name must be provided" in str(excinfo.value)
        finally:
            if hasattr(ops, "_operation_scope"):
                setattr(ops._operation_scope, "workspace_name", orig_workspace)
                setattr(ops._operation_scope, "registry_name", orig_registry)
            else:
                try:
                    ops._workspace_name = orig_workspace
                except Exception:
                    pass
                try:
                    ops._registry_name = orig_registry
                except Exception:
                    pass

    def test_divide_nodes_to_resolve_into_layers_with_single_leaf_node(self, client: MLClient) -> None:
        ops = client.components
        # create a minimal PipelineComponent and inject a single leaf job
        leaf = object()
        pc = PipelineComponent()
        try:
            # try to construct directly; some versions validate job types and will raise
            pc = PipelineComponent(jobs={"leaf_job": leaf})
        except Exception:
            # fallback to set internal jobs dict directly to exercise the splitting logic
            setattr(pc, "_jobs", {"leaf_job": leaf})

        layers = ops._divide_nodes_to_resolve_into_layers(pc, extra_operations=[])
        # Expect one layer containing the single leaf node
        assert isinstance(layers, list)
        assert len(layers) == 1
        assert len(layers[0]) == 1
        name, node = layers[0][0]
        assert name == "leaf_job"
        assert node is leaf
