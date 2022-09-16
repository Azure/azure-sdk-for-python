# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Dict, List, Union

from marshmallow import ValidationError

from azure.ai.ml._schema.pipeline.control_flow_job import DoWhileSchema
from azure.ai.ml.constants._component import DO_WHILE_MAX_ITERATION, ControlFlowType
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.job_limits import DoWhileJobLimits
from azure.ai.ml.entities._job.pipeline._io import InputOutputBase
from azure.ai.ml.exceptions import ErrorCategory, ValidationErrorType

from .._util import load_from_dict, validate_attribute_type
from .base_node import BaseNode
from .control_flow_node import LoopNode
from .pipeline import Pipeline

module_logger = logging.getLogger(__name__)


class DoWhile(LoopNode):
    """Do-while loop node in the pipeline job.
    By specifying the loop body and loop termination condition in this class, a job-level do while loop can be
    implemented.
    It will be initialized when calling dsl.do_while or when loading the pipeline yml containing do_while node.
    Please do not manually initialize this class.

    :param body: Pipeline job for the do-while loop body.
    :type body: Pipeline
    :param condition: Boolean type control output of body as do-while loop condition.
    :type condition: Output
    :param mapping: Output-Input mapping for reach round of the do-while loop.
                    Key is the last round output of the body. Value is the input port for current body.
    :type mapping: Dict[Union[str, Output], Union[str, Input, List]]
    :param limits: limits in running the do-while node.
    :type limits: DoWhileJobLimits
    """

    def __init__(
        self,
        *,
        body: Pipeline,
        condition: str,
        mapping: Dict[Union[str, Output], Union[str, Input, List]],
        limits: Union[dict, DoWhileJobLimits] = None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs.pop("type", None)
        super(DoWhile, self).__init__(
            type=ControlFlowType.DO_WHILE,
            body=body,
            **kwargs,
        )

        # init mark for _AttrDict
        self._init = True
        self._mapping = mapping or {}
        self._condition = condition
        self._limits = limits
        self._init = False

    @property
    def mapping(self):
        return self._mapping

    @property
    def condition(self):
        return self._condition

    @property
    def limits(self):
        return self._limits

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "mapping": dict,
            "limits": (dict, DoWhileJobLimits),
        }

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs):
        loaded_data = load_from_dict(DoWhileSchema, data, context, additional_message, **kwargs)

        return cls(**loaded_data)

    @classmethod
    def _create_instance_from_schema_dict(cls, pipeline_jobs, loaded_data: Dict, validate_port=True) -> "DoWhile":
        """Create a do_while instance from schema parsed dict."""

        # pylint: disable=protected-access

        def get_port_obj(body, port_name, is_input=True, validate_port=True):
            if is_input:
                port = body.inputs.get(port_name, None)
            else:
                port = body.outputs.get(port_name, None)
            if not port:
                if validate_port:
                    raise ValidationError(
                        message=f"Cannot find {port_name} in do_while loop body {'inputs' if is_input else 'outputs'}.",
                        target=cls._get_validation_error_target(),
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )
                return port_name

            return port

        # Get body object from pipeline job list.
        body_name = cls._get_data_binding_expression_value(loaded_data.pop("body"), regex=r"\{\{.*\.jobs\.(.*)\}\}")
        if body_name not in pipeline_jobs:
            raise ValidationError(
                message=f'Cannot find the do-while loop body "{body_name}" in the pipeline.',
                target=cls._get_validation_error_target(),
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        body = pipeline_jobs[body_name]

        # Convert mapping key-vault to input/output object
        mapping = {}
        for k, v in loaded_data.pop("mapping", {}).items():
            output_name = cls._get_data_binding_expression_value(k, regex=r"\{\{.*\.%s\.outputs\.(.*)\}\}" % body_name)
            input_names = v if isinstance(v, list) else [v]
            input_names = [
                cls._get_data_binding_expression_value(item, regex=r"\{\{.*\.%s\.inputs\.(.*)\}\}" % body_name)
                for item in input_names
            ]
            mapping[output_name] = [get_port_obj(body, item, validate_port=validate_port) for item in input_names]

        # Convert condition to output object
        condition_name = cls._get_data_binding_expression_value(
            loaded_data.pop("condition"), regex=r"\{\{.*\.%s\.outputs\.(.*)\}\}" % body_name
        )

        limits = loaded_data.pop("limits", None)
        do_while_instance = DoWhile(
            body=body,
            mapping=mapping,
            condition=get_port_obj(body, condition_name, is_input=False, validate_port=validate_port),
            **loaded_data,
        )
        do_while_instance.set_limits(**limits)
        # Update referenced control flow node instance id.
        body._set_referenced_control_flow_node_instance_id(do_while_instance._instance_id)
        return do_while_instance

    @classmethod
    def _create_schema_for_validation(cls, context):
        return DoWhileSchema(context=context)

    @classmethod
    def _from_rest_object(cls, obj: dict, reference_node_list: List) -> "DoWhile":
        # pylint: disable=protected-access

        obj = BaseNode._rest_object_to_init_params(obj)
        return cls._create_instance_from_schema_dict(reference_node_list, obj, validate_port=False)

    def set_limits(self, *, max_iteration_count: int, **kwargs):
        """Set max iteration count for do while job. The range of the iteration count is (0, 1000]."""
        if isinstance(self.limits, DoWhileJobLimits):
            self.limits.max_iteration_count = max_iteration_count
        else:
            self._limits = DoWhileJobLimits(max_iteration_count=max_iteration_count)

    def _get_body_binding_str(self):
        return "${{parent.jobs.%s}}" % self.body.name

    def _customized_validate(self):
        validation_result = self._validate_loop_condition(raise_error=False)
        validation_result.merge_with(self._validate_body(raise_error=False))
        validation_result.merge_with(self._validate_do_while_limit(raise_error=False))
        validation_result.merge_with(self._validate_body_output_mapping(raise_error=False))
        return validation_result

    def _validate_loop_condition(self, raise_error=True):
        # pylint: disable=protected-access

        validation_result = self._create_empty_validation_result()
        if not self.condition:
            validation_result.append_error(yaml_path="condition", message="The condition cannot be empty.")
        elif self.condition._name not in self.body.outputs:
            validation_result.append_error(
                yaml_path="condition", message=f"Cannot find the output {self.condition._name} in body outputs."
            )
        return validation_result.try_raise(self._get_validation_error_target(), raise_error=raise_error)

    def _validate_do_while_limit(self, raise_error=True):
        validation_result = self._create_empty_validation_result()
        if not self.limits or self.limits.max_iteration_count is None:
            return validation_result.try_raise(self._get_validation_error_target(), raise_error=raise_error)
        if isinstance(self.limits.max_iteration_count, InputOutputBase):
            validation_result.append_error(
                yaml_path="limit.max_iteration_count",
                message="The max iteration count cannot be linked with an primitive type input.",
            )
        elif self.limits.max_iteration_count > DO_WHILE_MAX_ITERATION or self.limits.max_iteration_count < 0:
            validation_result.append_error(
                yaml_path="limit.max_iteration_count",
                message=f"The max iteration count cannot be less than 0 and larger than {DO_WHILE_MAX_ITERATION}.",
            )
        return validation_result.try_raise(self._get_validation_error_target(), raise_error=raise_error)

    def _validate_body_output_mapping(self, raise_error=True):
        # pylint disable=protected-access
        validation_result = self._create_empty_validation_result()
        if not self.mapping:
            validation_result.append_error(
                yaml_path="mapping", message="The mapping of body output to input cannot be empty."
            )
        elif not isinstance(self.mapping, dict):
            validation_result.append_error(
                yaml_path="mapping", message=f"Mapping expects a dict type but passes in a {type(self.mapping)} type."
            )
        else:
            # Validate mapping input&output should come from while body
            for k, v in self.mapping.items():
                if k not in self.body.outputs:
                    validation_result.append_error(
                        yaml_path="mapping",
                        message=f"The key of mapping {k} does not exist in {self.body.name} outputs, "
                        f"exist outputs: {self.body.outputs.keys()}",
                    )

                else:
                    v = v if isinstance(v, list) else [v]
                    for item in v:
                        if item not in self.body.inputs.values():
                            validation_result.append_error(
                                yaml_path="mapping",
                                message=f"The value of mapping {item._name} does not exist in {self.body.name} "
                                f"inputs, exist inputs: {self.body.inputs.keys()}",
                            )
        return validation_result.try_raise(self._get_validation_error_target(), raise_error=raise_error)
