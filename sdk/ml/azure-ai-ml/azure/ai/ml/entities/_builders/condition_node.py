# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.constants._component import ControlFlowType
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.pipeline._io import InputOutputBase
from azure.ai.ml.entities._validation import MutableValidationResult


class ConditionNode(ControlFlowNode):
    """
    Conditional node in pipeline. Please do not directly use this class.
    """

    def __init__(self, condition, true_block, false_block, **kwargs):  # pylint: disable=unused-argument
        kwargs.pop("type", None)
        super(ConditionNode, self).__init__(type=ControlFlowType.IF_ELSE, **kwargs)
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

    @classmethod
    def _create_schema_for_validation(
        cls, context
    ) -> PathAwareSchema:  # pylint: disable=unused-argument
        from azure.ai.ml._schema.pipeline.condition_node import ConditionNodeSchema

        return ConditionNodeSchema(context=context)

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "ConditionNode":
        return cls(**obj)

    def _to_dict(self) -> Dict:
        return self._dump_for_validation()

    def _customized_validate(self) -> MutableValidationResult:
        return self._validate_params(raise_error=False)

    def _validate_params(self, raise_error=True) -> MutableValidationResult:
        # pylint disable=protected-access
        validation_result = self._create_empty_validation_result()
        if not isinstance(self.condition, (str, bool, InputOutputBase)):
            validation_result.append_error(
                yaml_path="condition",
                message=f"'condition' of dsl.condition node must be an instance of "
                f"{str}, {bool} or {InputOutputBase}, got {type(self.condition)}.",
            )

        # Check if output is a control output.
        # pylint: disable=protected-access
        if isinstance(self.condition, InputOutputBase) and self.condition._meta is not None:
            # pylint: disable=protected-access
            output_definition = self.condition._meta
            if output_definition is not None and not output_definition.is_control:
                validation_result.append_error(
                    yaml_path="condition",
                    message=f"'condition' of dsl.condition node must have 'is_control' field "
                    f"with value 'True', got {output_definition.is_control}",
                )

        error_msg = "{!r} of dsl.condition node must be an instance of " f"{BaseNode} or {AutoMLJob}," "got {!r}."
        if self.true_block is not None and not isinstance(self.true_block, (BaseNode, AutoMLJob)):
            validation_result.append_error(
                yaml_path="true_block", message=error_msg.format("true_block", type(self.true_block))
            )
        if self.false_block is not None and not isinstance(self.false_block, (BaseNode, AutoMLJob)):
            validation_result.append_error(
                yaml_path="false_block", message=error_msg.format("false_block", type(self.false_block))
            )

        if self.true_block is None and self.false_block is None:
            validation_result.append_error(
                yaml_path="true_block",
                message="'true_block' and 'false_block' of dsl.condition node cannot both be None.",
            )
        elif self.true_block is self.false_block:
            validation_result.append_error(
                yaml_path="true_block",
                message="'true_block' and 'false_block' of dsl.condition node cannot be the same object.",
            )

        return validation_result.try_raise(self._get_validation_error_target(), raise_error=raise_error)
