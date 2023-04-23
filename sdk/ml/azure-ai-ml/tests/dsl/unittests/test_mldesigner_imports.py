import pytest
from azure.ai.ml import Input
from azure.ai.ml.entities import (
    Component,
    CommandComponent,
    PipelineComponent,
    ValidationResult,
)
from azure.ai.ml.dsl._mldesigner import (
    InternalAdditionalIncludes,
    InternalComponent,
    ParallelFor,
)
from azure.ai.ml.entities._builders.base_node import BaseNode
from azure.ai.ml.entities._inputs_outputs import GroupInput
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, NodeOutput, NodeInput


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
        assert hasattr(InternalAdditionalIncludes, "with_includes")
        assert hasattr(InternalAdditionalIncludes, "code_path")
        assert hasattr(InternalAdditionalIncludes, "includes")
        assert hasattr(ValidationResult, "passed")
        assert hasattr(ValidationResult, "error_messages")
        assert hasattr(ParallelFor, "_to_rest_items")

    def test_necessary_attributes_for_input(self):
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

        node_input_obj = NodeInput(port_name="sdk", meta=input_obj)
        assert hasattr(node_input_obj, "_meta")
        assert hasattr(node_input_obj, "_data")

    def test_class_names(self):
        """These class are undirectly used in mldesigner by their class names"""
        assert BaseNode.__name__ == "BaseNode"
        assert GroupInput.__name__ == "GroupInput"
        assert PipelineInput.__name__ == "PipelineInput"
        assert NodeInput.__name__ == "NodeInput"
        assert NodeOutput.__name__ == "NodeOutput"
