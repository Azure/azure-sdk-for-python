# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union

from azure.ai.ml import Output
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.control_flow_job import ParallelForSchema
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._component import ComponentParameterTypes, ControlFlowType
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.control_flow_node import LoopNode
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, validate_attribute_type
from azure.ai.ml.exceptions import UserErrorException


class ParallelFor(LoopNode, NodeIOMixin):
    """Parallel for loop node in the pipeline job.
    By specifying the loop body and aggregated items, a job-level parallel for loop can be implemented.
    It will be initialized when calling dsl.parallel_for or when loading the pipeline yml containing parallel_for node.
    Please do not manually initialize this class.

    :param body: Pipeline job for the parallel for loop body.
    :type body: Pipeline
    :param items: The loop body's input which will bind to the loop node.
    :type items: Union[list, dict, str, PipelineInput, NodeOutput]
    :param max_concurrency: Maximum number of concurrent iterations to run. All loop body nodes will be executed
        in parallel if not specified.
    :type max_concurrency: int
    """

    OUT_TYPE_MAPPING = {
        AssetTypes.URI_FILE: AssetTypes.MLTABLE,
        AssetTypes.URI_FOLDER: AssetTypes.MLTABLE,
        AssetTypes.MLTABLE: AssetTypes.MLTABLE,
        AssetTypes.MLFLOW_MODEL: AssetTypes.MLTABLE,
        AssetTypes.TRITON_MODEL: AssetTypes.MLTABLE,
        AssetTypes.CUSTOM_MODEL: AssetTypes.MLTABLE,
        # legacy path support
        "path": AssetTypes.MLTABLE,
        ComponentParameterTypes.NUMBER: ComponentParameterTypes.STRING,
        ComponentParameterTypes.STRING: ComponentParameterTypes.STRING,
        ComponentParameterTypes.BOOLEAN: ComponentParameterTypes.STRING,
        ComponentParameterTypes.INTEGER: ComponentParameterTypes.STRING,
    }

    def __init__(
        self,
        *,
        body,
        items,
        max_concurrency=None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs.pop("type", None)
        super(ParallelFor, self).__init__(
            type=ControlFlowType.PARALLEL_FOR,
            body=body,
            **kwargs,
        )
        # loop body is incomplete in submission time, so won't validate required inputs
        self.body._validate_required_input_not_provided = False

        actual_outputs = kwargs.get("outputs", {})
        # parallel for node shares output meta with body
        try:
            outputs = self.body._component.outputs
            # transform body outputs to aggregate types when available
            self._outputs = self._build_outputs_dict(
                output_definition_dict=self._convert_output_meta(outputs), outputs=actual_outputs
            )
        except AttributeError:
            # when body output not available, create default output builder without meta
            self._outputs = self._build_outputs_dict_without_meta(outputs=actual_outputs)

        self._items = items

        self.max_concurrency = max_concurrency

    @property
    def outputs(self) -> Dict[str, Union[str, Output]]:
        return self._outputs

    @property
    def items(self):
        """The loop body's input which will bind to the loop node."""
        return self._items

    @classmethod
    def _create_schema_for_validation(cls, context) -> PathAwareSchema:
        return ParallelForSchema(context=context)

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            **super(ParallelFor, cls)._attr_type_map(),
            "items": (dict, list, str, PipelineInput, NodeOutput),
        }

    def _to_rest_object(self, **kwargs) -> dict:  # pylint: disable=unused-argument
        """Convert self to a rest object for remote call."""
        rest_node = super(ParallelFor, self)._to_rest_object(**kwargs)
        rest_node.update(dict(outputs=self._to_rest_outputs()))
        return convert_ordered_dict_to_dict(rest_node)

    @classmethod
    def _from_rest_object(cls, obj: dict, pipeline_jobs: dict) -> "ParallelFor":
        # pylint: disable=protected-access

        obj = BaseNode._from_rest_object_to_init_params(obj)
        return cls._create_instance_from_schema_dict(pipeline_jobs=pipeline_jobs, loaded_data=obj)

    @classmethod
    def _create_instance_from_schema_dict(cls, pipeline_jobs, loaded_data, **kwargs):
        body_name = cls._get_data_binding_expression_value(loaded_data.pop("body"), regex=r"\{\{.*\.jobs\.(.*)\}\}")

        loaded_data["body"] = cls._get_body_from_pipeline_jobs(pipeline_jobs=pipeline_jobs, body_name=body_name)
        return cls(**loaded_data, **kwargs)

    def _convert_output_meta(self, outputs):
        """Convert output meta to aggregate types."""
        # pylint: disable=protected-access
        aggregate_outputs = {}
        for name, output in outputs.items():
            if output.type in self.OUT_TYPE_MAPPING:
                new_type = self.OUT_TYPE_MAPPING[output.type]
            else:
                # when loop body introduces some new output type, this will be raised as a reminder to support is in
                # parallel for
                raise UserErrorException(
                    "Referencing output with type {} is not supported in parallel_for node.".format(output.type)
                )
            if isinstance(output, NodeOutput):
                output = output._to_job_output()
            if isinstance(output, Output):
                out_dict = output._to_dict()
                out_dict["type"] = new_type
                resolved_output = Output(**out_dict)
            else:
                resolved_output = Output(type=new_type)
            aggregate_outputs[name] = resolved_output
        return aggregate_outputs

    def _validate_items(self, raise_error=True):
        validation_result = self._create_empty_validation_result()
        if self.items is not None:
            items = self.items
            if isinstance(items, str):
                # try to deserialize str if it's a json string
                try:
                    items = json.loads(items)
                except json.JSONDecodeError as e:
                    if not is_data_binding_expression(items, ["parent"]):
                        validation_result.append_error(
                            yaml_path="items",
                            message=f"Items is neither a valid JSON string due to {e} or a binding string."
                        )
            if isinstance(items, dict):
                # Validate dict keys
                items = list(items.values())
            if isinstance(items, list):
                if len(items) > 0:
                    self._validate_items_list(items, validation_result)
                else:
                    validation_result.append_error(
                        yaml_path="items",
                        message="Items is an empty list/dict.")
        else:
            validation_result.append_error(
                yaml_path="items",
                message="Items is required for parallel_for node",
            )
        return validation_result.try_raise(
            self._get_validation_error_target(),
            raise_error=raise_error,
        )

    def _customized_validate(self):
        """Customized validation for parallel for node."""
        validation_result = self._validate_body(raise_error=False)
        validation_result.merge_with(self._validate_items(raise_error=False))
        return validation_result

    def _validate_items_list(self, items: list, validation_result):
        # pylint: disable=protected-access
        meta = {}
        # all items have to be dict and have matched meta
        for item in items:
            # item has to be dict
            # Note: item can be empty dict when loop_body don't have foreach inputs.
            if not isinstance(item, dict):
                validation_result.append_error(
                    yaml_path="items",
                    message=f"Items has to be list/dict of dict as value, " f"but got {type(item)} for {item}."
                )
            else:
                # item has to have matched meta
                if meta.keys() != item.keys():
                    if not meta.keys():
                        meta = item
                    else:
                        msg = f"Items should have same keys with body inputs, but got {item.keys()} and {meta.keys()}."
                        validation_result.append_error(
                            yaml_path="items",
                            message=msg
                        )
                # items' keys should appear in body's inputs
                body_component = self.body._component
                if isinstance(body_component, Component) and (not item.keys() <= body_component.inputs.keys()):
                    msg = f"Item {item} got unmatched inputs with loop body component inputs {body_component.inputs}."
                    validation_result.append_error(
                        yaml_path="items",
                        message=msg
                    )
