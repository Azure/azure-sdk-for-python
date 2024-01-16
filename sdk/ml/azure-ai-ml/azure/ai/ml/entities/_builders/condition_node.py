# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, List, Optional

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants._component import ControlFlowType
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.pipeline._io import InputOutputBase
from azure.ai.ml.entities._validation import MutableValidationResult


class ConditionNode(ControlFlowNode):
    """Conditional node in the pipeline.

    Please do not directly use this class.

    :param condition: The condition for the conditional node.
    :type condition: Any
    :param true_block: The list of nodes to execute when the condition is true.
    :type true_block: List[~azure.ai.ml.entities._builders.BaseNode]
    :param false_block: The list of nodes to execute when the condition is false.
    :type false_block: List[~azure.ai.ml.entities._builders.BaseNode]
    """

    def __init__(
        self, condition: Any, *, true_block: Optional[List] = None, false_block: Optional[List] = None, **kwargs: Any
    ) -> None:  # pylint: disable=unused-argument
        kwargs.pop("type", None)
        super(ConditionNode, self).__init__(type=ControlFlowType.IF_ELSE, **kwargs)
        self.condition = condition
        if true_block and not isinstance(true_block, list):
            true_block = [true_block]
        self._true_block = true_block
        if false_block and not isinstance(false_block, list):
            false_block = [false_block]
        self._false_block = false_block

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> PathAwareSchema:  # pylint: disable=unused-argument
        from azure.ai.ml._schema.pipeline.condition_node import ConditionNodeSchema

        return ConditionNodeSchema(context=context)

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "ConditionNode":
        return cls(**obj)

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "ConditionNode":
        """Create a condition node instance from schema parsed dict.

        :param loaded_data: The loaded data
        :type loaded_data: Dict
        :return: The ConditionNode node
        :rtype: ConditionNode
        """
        return cls(**loaded_data)

    @property
    def true_block(self) -> Optional[List]:
        """Get the list of nodes to execute when the condition is true.

        :return: The list of nodes to execute when the condition is true.
        :rtype: List[~azure.ai.ml.entities._builders.BaseNode]
        """
        return self._true_block

    @property
    def false_block(self) -> Optional[List]:
        """Get the list of nodes to execute when the condition is false.

        :return: The list of nodes to execute when the condition is false.
        :rtype: List[~azure.ai.ml.entities._builders.BaseNode]
        """
        return self._false_block

    def _customized_validate(self) -> MutableValidationResult:
        return self._validate_params()

    def _validate_params(self) -> MutableValidationResult:
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
            if output_definition is not None and not output_definition._is_primitive_type:
                validation_result.append_error(
                    yaml_path="condition",
                    message=f"'condition' of dsl.condition node must be primitive type "
                    f"with value 'True', got {output_definition._is_primitive_type}",
                )

        # check if condition is valid binding
        if isinstance(self.condition, str) and not is_data_binding_expression(
            self.condition, ["parent"], is_singular=False
        ):
            error_tail = "for example, ${{parent.jobs.xxx.outputs.output}}"
            validation_result.append_error(
                yaml_path="condition",
                message=f"'condition' of dsl.condition has invalid binding expression: {self.condition}, {error_tail}",
            )

        error_msg = (
            "{!r} of dsl.condition node must be an instance of " f"{BaseNode}, {AutoMLJob} or {str}," "got {!r}."
        )
        blocks = self.true_block if self.true_block else []
        for block in blocks:
            if block is not None and not isinstance(block, (BaseNode, AutoMLJob, str)):
                validation_result.append_error(
                    yaml_path="true_block", message=error_msg.format("true_block", type(block))
                )
        blocks = self.false_block if self.false_block else []
        for block in blocks:
            if block is not None and not isinstance(block, (BaseNode, AutoMLJob, str)):
                validation_result.append_error(
                    yaml_path="false_block", message=error_msg.format("false_block", type(block))
                )

        # check if true/false block is valid binding
        for name, blocks in {"true_block": self.true_block, "false_block": self.false_block}.items():  # type: ignore
            blocks = blocks if blocks else []
            for block in blocks:
                if block is None or not isinstance(block, str):
                    continue
                error_tail = "for example, ${{parent.jobs.xxx}}"
                if not is_data_binding_expression(block, ["parent", "jobs"], is_singular=False):
                    validation_result.append_error(
                        yaml_path=name,
                        message=f"'{name}' of dsl.condition has invalid binding expression: {block}, {error_tail}",
                    )

        return validation_result
