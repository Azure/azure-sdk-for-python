# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Dict, List, Optional, Union

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
    """Do-while loop node in the pipeline job. By specifying the loop body and loop termination condition in this class,
    a job-level do while loop can be implemented. It will be initialized when calling dsl.do_while or when loading the
    pipeline yml containing do_while node. Please do not manually initialize this class.

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
        limits: Optional[Union[dict, DoWhileJobLimits]] = None,
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
            **super(DoWhile, cls)._attr_type_map(),
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
            if port is None:
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
        body = cls._get_body_from_pipeline_jobs(pipeline_jobs, body_name)

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

        limits = loaded_data.pop("limits", None)

        if "condition" in loaded_data:
            # Convert condition to output object
            condition_name = cls._get_data_binding_expression_value(
                loaded_data.pop("condition"), regex=r"\{\{.*\.%s\.outputs\.(.*)\}\}" % body_name
            )
            condition_value = get_port_obj(body, condition_name, is_input=False, validate_port=validate_port)
        else:
            condition_value = None

        do_while_instance = DoWhile(
            body=body,
            mapping=mapping,
            condition=condition_value,
            **loaded_data,
        )
        do_while_instance.set_limits(**limits)

        return do_while_instance

    @classmethod
    def _create_schema_for_validation(cls, context):
        return DoWhileSchema(context=context)

    @classmethod
    def _from_rest_object(cls, obj: dict, pipeline_jobs: dict) -> "DoWhile":
        # pylint: disable=protected-access

        obj = BaseNode._from_rest_object_to_init_params(obj)
        return cls._create_instance_from_schema_dict(pipeline_jobs, obj, validate_port=False)

    def set_limits(
        self,
        *,
        max_iteration_count: int,
        **kwargs,  # pylint: disable=unused-argument
    ):
        """Set max iteration count for do while job.

        The range of the iteration count is (0, 1000].
        """
        if isinstance(self.limits, DoWhileJobLimits):
            self.limits._max_iteration_count = max_iteration_count  # pylint: disable=protected-access
        else:
            self._limits = DoWhileJobLimits(max_iteration_count=max_iteration_count)

    def _customized_validate(self):
        validation_result = self._validate_loop_condition(raise_error=False)
        validation_result.merge_with(self._validate_body(raise_error=False))
        validation_result.merge_with(self._validate_do_while_limit(raise_error=False))
        validation_result.merge_with(self._validate_body_output_mapping(raise_error=False))
        return validation_result

    def _validate_port(self, port, node_ports, port_type, yaml_path):
        """Validate input/output port is exist in the dowhile body."""
        validation_result = self._create_empty_validation_result()
        if isinstance(port, str):
            port_obj = node_ports.get(port, None)
        else:
            port_obj = port
        if (
            port_obj is not None
            and port_obj._owner._instance_id != self.body._instance_id  # pylint: disable=protected-access
        ):
            # Check the port owner is dowhile body.
            validation_result.append_error(
                yaml_path=yaml_path,
                message=(
                    f"{port_obj._port_name} is the {port_type} of {port_obj._owner.name}, "  # pylint: disable=protected-access
                    f"dowhile only accept {port_type} of the body: {self.body.name}."
                ),
            )
        elif port_obj is None or port_obj._port_name not in node_ports:  # pylint: disable=protected-access
            # Check port is exist in dowhile body.
            validation_result.append_error(
                yaml_path=yaml_path,
                message=(
                    f"The {port_type} of mapping {port_obj._port_name if port_obj else port} does not "  # pylint: disable=protected-access
                    f"exist in {self.body.name} {port_type}, existing {port_type}: {node_ports.keys()}"
                ),
            )
        return validation_result

    def _validate_loop_condition(self, raise_error=True):
        # pylint: disable=protected-access
        validation_result = self._create_empty_validation_result()
        if self.condition is not None:
            # Check condition exists in dowhile body.
            validation_result.merge_with(
                self._validate_port(self.condition, self.body.outputs, port_type="output", yaml_path="condition")
            )
            if validation_result.passed:
                # Check condition is a control output.
                condition_name = self.condition if isinstance(self.condition, str) else self.condition._port_name
                if not self.body._outputs[condition_name].is_control:
                    validation_result.append_error(
                        yaml_path="condition",
                        message=(
                            f"{condition_name} is not a control output. "
                            "The condition of dowhile must be the control output of the body."
                        ),
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
                message=f"The max iteration count cannot be less than 0 or larger than {DO_WHILE_MAX_ITERATION}.",
            )
        return validation_result.try_raise(self._get_validation_error_target(), raise_error=raise_error)

    def _validate_body_output_mapping(self, raise_error=True):
        # pylint disable=protected-access
        validation_result = self._create_empty_validation_result()
        if not isinstance(self.mapping, dict):
            validation_result.append_error(
                yaml_path="mapping", message=f"Mapping expects a dict type but passes in a {type(self.mapping)} type."
            )
        else:
            # Record the mapping relationship between input and output
            input_output_mapping = {}
            # Validate mapping input&output should come from while body
            for output, inputs in self.mapping.items():
                # pylint: disable=protected-access
                output_name = output if isinstance(output, str) else output._port_name
                validate_results = self._validate_port(
                    output, self.body.outputs, port_type="output", yaml_path="mapping"
                )
                if validate_results.passed:
                    is_control_output = self.body._outputs[output_name].is_control
                    inputs = inputs if isinstance(inputs, list) else [inputs]
                    for item in inputs:
                        input_validate_results = self._validate_port(
                            item, self.body.inputs, port_type="input", yaml_path="mapping"
                        )
                        validation_result.merge_with(input_validate_results)
                        # pylint: disable=protected-access
                        input_name = item if isinstance(item, str) else item._port_name
                        input_output_mapping[input_name] = input_output_mapping.get(input_name, []) + [output_name]
                        is_primitive_type = self.body._inputs[input_name]._meta._is_primitive_type

                        if (
                            input_validate_results.passed
                            and not is_control_output
                            and is_primitive_type  # pylint: disable=protected-access
                        ):
                            validate_results.append_error(
                                yaml_path="mapping",
                                message=(
                                    f"{output_name} is a non-primitive type output and {input_name} "
                                    "is a primitive input. Non-primitive type output cannot be connected "
                                    "to an a primitive type input.",
                                ),
                            )

                validation_result.merge_with(validate_results)
            # Validate whether input is linked to multiple outputs
            for _input, outputs in input_output_mapping.items():
                if len(outputs) > 1:
                    validation_result.append_error(
                        yaml_path="mapping", message=f"Input {_input} has been linked to multiple outputs {outputs}."
                    )
        return validation_result.try_raise(self._get_validation_error_target(), raise_error=raise_error)
