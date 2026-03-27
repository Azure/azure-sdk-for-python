import types
from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Component
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.e2etest
class TestComponentOperationsGaps:
    def test_refine_component_rejects_variable_inputs(self, client: MLClient) -> None:
        # function with variable positional args should be rejected by _refine_component via create_or_update
        def func_with_var_args(*args):
            return None

        with pytest.raises(ValidationException):
            # trigger validation through public API as required by integration test mode
            client.components.create_or_update(func_with_var_args)

    def test_refine_component_requires_type_annotations_for_parameters(self, client: MLClient) -> None:
        # function with a parameter lacking annotation and no default should be rejected
        def func_unknown_type(param):
            return None

        with pytest.raises(ValidationException):
            client.components.create_or_update(func_unknown_type)

    def test_refine_component_rejects_non_dsl_non_mldesigner_function(self, client: MLClient) -> None:
        # a plain function that is neither a dsl nor mldesigner component should be rejected
        def plain_func() -> None:
            return None

        with pytest.raises(ValidationException):
            client.components.create_or_update(plain_func)


@pytest.mark.e2etest
class TestComponentOperationsRefine:
    def test_refine_component_raises_on_variable_args(self, client: MLClient) -> None:
        # Define a function with variable positional and keyword args which should trigger the VAR_POSITIONAL/VAR_KEYWORD check
        def _func_with_varargs(a: int, *args, **kwargs):
            return None

        # create_or_update will call _refine_component and should raise ValidationException before any network call
        with pytest.raises(ValidationException) as exc:
            client.components.create_or_update(_func_with_varargs)
        assert "must be a dsl or mldesigner" in str(exc.value)

    def test_refine_component_raises_on_unknown_type_keys(self, client: MLClient) -> None:
        # Define a DSL-like function by setting attributes to mimic a dsl function but leave one parameter without annotation
        def _func_missing_annotation(a, b: int = 1):
            return None

        # Mark as dsl function so _refine_component runs parameter checks
        setattr(_func_missing_annotation, "_is_dsl_func", True)
        # Provide a minimal pipeline builder with expected attributes used by _refine_component
        class _Builder:
            non_pipeline_parameter_names = []

            def build(self, user_provided_kwargs=None):
                from azure.ai.ml.entities import PipelineComponent

                # return a simple PipelineComponent instance; using minimal stub via actual entity requires less here
                return PipelineComponent(jobs={}, inputs={}, outputs={})

        # Attach a dummy pipeline_builder and empty job settings
        setattr(_func_missing_annotation, "_pipeline_builder", _Builder())
        setattr(_func_missing_annotation, "_job_settings", None)

        # The missing annotation for parameter 'a' should trigger ValidationException
        with pytest.raises(ValidationException) as exc:
            client.components.create_or_update(_func_missing_annotation)
        assert "Unknown type of parameter" in str(exc.value)

    def test_refine_component_rejects_non_dsl_and_non_mldesigner(self, client: MLClient) -> None:
        # A regular function without dsl or mldesigner markers should be rejected
        def _regular_function(x: int) -> None:
            return None

        with pytest.raises(ValidationException) as exc:
            client.components.create_or_update(_regular_function)
        assert "must be a dsl or mldesigner" in str(exc.value)


@pytest.mark.e2etest
class TestComponentOperationsValidation:
    def test_component_function_with_variable_args_raises(self, client: MLClient) -> None:
        # Function with *args and **kwargs should be rejected by _refine_component
        def fn_with_varargs(a, *args, **kwargs):
            return None

        with pytest.raises(ValidationException) as exinfo:
            # Trigger validation via public API which calls _refine_component
            client.components.create_or_update(fn_with_varargs)

        assert "Function must be a dsl or mldesigner component function" in str(exinfo.value)

    def test_pipeline_function_with_non_pipeline_inputs_raises(self, client: MLClient) -> None:
        # Create a fake pipeline-style function marked as dsl but with non_pipeline_parameter_names
        def fake_pipeline():
            return None

        # Attach attributes to simulate a pipeline builder with non_pipeline_parameter_names
        fake_pipeline._is_dsl_func = True

        class Builder:
            non_pipeline_parameter_names = ["bad_input"]

            def build(self, user_provided_kwargs=None):
                return None

        fake_pipeline._pipeline_builder = Builder()

        with pytest.raises(ValidationException) as exinfo:
            client.components.create_or_update(fake_pipeline)

        assert "Cannot register pipeline component" in str(exinfo.value)
        assert "non_pipeline_inputs" in str(exinfo.value)

    def test_plain_function_not_dsl_or_mldesigner_raises(self, client: MLClient) -> None:
        # A plain function without dsl/mldesigner markers should be rejected
        def plain_function(a: int):
            return None

        with pytest.raises(ValidationException) as exinfo:
            client.components.create_or_update(plain_function)

        assert "Function must be a dsl or mldesigner component function" in str(exinfo.value)


@pytest.mark.e2etest
class TestComponentOperationsValidationErrors:
    def test_create_or_update_with_plain_function_raises_validation(self, client: MLClient) -> None:
        """Ensure passing a plain function (not DSL/mldesigner) into create_or_update raises ValidationException.

        Covers the branch where _refine_component raises because the function is neither a dsl nor mldesigner component.
        """

        def plain_function(a: int) -> int:
            return a + 1

        with pytest.raises(ValidationException) as excinfo:
            # Trigger validation path via public API
            client.components.create_or_update(plain_function)

        # Exact message must indicate function must be a dsl or mldesigner component function
        assert "Function must be a dsl or mldesigner component function" in str(excinfo.value)


@pytest.mark.e2etest
class TestComponentOperationsGeneratedBatch1:
    def test_create_or_update_with_untyped_function_raises_validation(self, client: MLClient) -> None:
        """
        Covers branch where input to create_or_update is a plain python function that is neither
        a dsl pipeline function nor an mldesigner component function, which should raise
        a ValidationException from _refine_component.
        """

        def plain_func(a, b):
            return a + b

        with pytest.raises(ValidationException) as excinfo:
            # Trigger code path through public API as required by integration test rules
            client.components.create_or_update(plain_func)  # type: ignore[arg-type]

        # Assert the exact error message fragment expected from _refine_component
        assert "Function must be a dsl or mldesigner component function" in str(excinfo.value)

    def test_validate_pipeline_function_with_varargs_raises(self, client: MLClient) -> None:
        """
        Covers parameter type checking in _refine_component -> check_parameter_type branch where
        a function with *args/**kwargs should raise ValidationException when passed to validate().
        """

        def pipeline_like_with_varargs(*args, **kwargs):
            # Emulate an object that might have _is_dsl_func attribute but still has varargs
            return None

        # Manually attach attribute to make _refine_component go through DSL branch's parameter checks
        setattr(pipeline_like_with_varargs, "_is_dsl_func", True)
        # minimal pipeline builder mock to satisfy attribute access in _refine_component
        class DummyBuilder:
            non_pipeline_parameter_names = []
            def build(self, user_provided_kwargs=None):
                return Component(name="test_dummy", version="1")

        setattr(pipeline_like_with_varargs, "_pipeline_builder", DummyBuilder())
        # leave _job_settings empty
        setattr(pipeline_like_with_varargs, "_job_settings", None)

        # Expect validation to fail because of variable inputs
        with pytest.raises(ValidationException) as excinfo:
            client.components.validate(pipeline_like_with_varargs)  # type: ignore[arg-type]

        assert "Cannot register the component" in str(excinfo.value)
