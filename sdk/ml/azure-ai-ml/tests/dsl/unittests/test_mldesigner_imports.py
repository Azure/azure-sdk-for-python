import pytest
from azure.ai.ml import Input
from azure.ai.ml.entities import(
    Component,
    CommandComponent,
    PipelineComponent,
    ValidationResult,
)
from azure.ai.ml.dsl._mldesigner import(
    _AdditionalIncludes,
    InternalComponent,
    ErrorTarget,
)

@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestMldesignerImports:
    """
    The assertions are NOT SUPPOSED TO BE CHANGED once they are added.

    The attributes are needed for a certain version of mldesigner package, modifying or deleting any of them will cause
    compatibility issues. If there are new dependencies for mldesigner package, add new assertions in this file.
    """
    def test_necessay_attributes(self):
        assert hasattr(Component, "_customized_validate")
        assert hasattr(Component, "_source_path")
        assert hasattr(CommandComponent, "_to_dict")
        assert hasattr(CommandComponent, "_source_path")
        assert hasattr(PipelineComponent, "_to_dict")
        assert hasattr(PipelineComponent, "_source_path")
        assert hasattr(PipelineComponent, "jobs")
        assert hasattr(InternalComponent, "_to_dict")
        assert hasattr(InternalComponent, "_source_path")
        assert hasattr(InternalComponent, "_additional_includes")
        assert hasattr(_AdditionalIncludes, "with_includes")
        assert hasattr(_AdditionalIncludes, "_code_path")
        assert hasattr(_AdditionalIncludes, "_includes")
        assert hasattr(ValidationResult, "passed")
        assert hasattr(ValidationResult, "error_messages")
        assert hasattr(ErrorTarget, "PIPELINE")

    def test_necessay_attributes_for_input(self):
        input_obj = Input()
        assert hasattr(input_obj, "type")
        assert hasattr(input_obj, "_is_enum")
        assert hasattr(input_obj, "default")
        assert hasattr(input_obj, "min")
        assert hasattr(input_obj, "max")
        assert hasattr(input_obj, "optional")
        assert hasattr(input_obj, "_is_literal")
        assert hasattr(input_obj, "_get_python_builtin_type_str")
        assert hasattr(input_obj, "_get_param_with_standard_annotation")
