# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
from typing import Any, Dict, Optional, Union

from azure.ai.ml import Input, Output
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.control_flow_job import ParallelForSchema
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._component import ComponentParameterTypes, ControlFlowType
from azure.ai.ml.entities import Component, Pipeline
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.control_flow_node import LoopNode
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, validate_attribute_type
from azure.ai.ml.entities._validation import MutableValidationResult
from azure.ai.ml.exceptions import UserErrorException


class ParallelFor(LoopNode, NodeIOMixin):
    """Parallel for loop node in the pipeline job. By specifying the loop body and aggregated items, a job-level
    parallel for loop can be implemented. It will be initialized when calling dsl.parallel_for or when loading the
    pipeline yml containing parallel_for node. Please do not manually initialize this class.

    :param body: Pipeline job for the parallel for loop body.
    :type body: ~azure.ai.ml.entities.Pipeline
    :param items: The loop body's input which will bind to the loop node.
    :type items: typing.Union[list, dict, str, ~azure.ai.ml.entities._job.pipeline._io.NodeOutput,
        ~azure.ai.ml.entities._job.pipeline._io.PipelineInput]
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
        body: "Pipeline",
        items: Union[list, dict, str, PipelineInput, NodeOutput],
        max_concurrency: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
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
        self._outputs: dict = {}

        actual_outputs = kwargs.get("outputs", {})
        # parallel for node shares output meta with body
        try:
            outputs = self.body._component.outputs
            # transform body outputs to aggregate types when available
            self._outputs = self._build_outputs_dict(
                outputs=actual_outputs, output_definition_dict=self._convert_output_meta(outputs)
            )
        except AttributeError:
            # when body output not available, create default output builder without meta
            self._outputs = self._build_outputs_dict(outputs=actual_outputs)

        self._items = items

        self.max_concurrency = max_concurrency

    @property
    def outputs(self) -> Dict[str, Union[str, Output]]:
        """Get the outputs of the parallel for loop.

        :return: The dictionary containing the outputs of the parallel for loop.
        :rtype: dict[str, Union[str, ~azure.ai.ml.Output]]
        """
        return self._outputs

    @property
    def items(self) -> Union[list, dict, str, PipelineInput, NodeOutput]:
        """Get the loop body's input which will bind to the loop node.

        :return: The input for the loop body.
        :rtype: typing.Union[list, dict, str, ~azure.ai.ml.entities._job.pipeline._io.NodeOutput,
            ~azure.ai.ml.entities._job.pipeline._io.PipelineInput]
        """
        return self._items

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> PathAwareSchema:
        return ParallelForSchema(context=context)

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            **super(ParallelFor, cls)._attr_type_map(),
            "items": (dict, list, str, PipelineInput, NodeOutput),
        }

    @classmethod
    # pylint: disable-next=docstring-missing-param
    def _to_rest_item(cls, item: dict) -> dict:
        """Convert item to rest object.

        :return: The rest object
        :rtype: dict
        """
        primitive_inputs, asset_inputs = {}, {}
        # validate item
        for key, val in item.items():
            if isinstance(val, Input):
                asset_inputs[key] = val
            elif isinstance(val, (PipelineInput, NodeOutput)):
                # convert binding object to string
                primitive_inputs[key] = str(val)
            else:
                primitive_inputs[key] = val
        return {
            # asset type inputs will be converted to JobInput dict:
            # {"asset_param": {"uri": "xxx", "job_input_type": "uri_file"}}
            **cls._input_entity_to_rest_inputs(input_entity=asset_inputs),
            # primitive inputs has primitive type value like this
            # {"int_param": 1}
            **primitive_inputs,
        }

    @classmethod
    # pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
    def _to_rest_items(cls, items: Union[list, dict, str, NodeOutput, PipelineInput]) -> str:
        """Convert items to rest object."""
        # validate items.
        cls._validate_items(items=items, raise_error=True, body_component=None)
        result: str = ""
        # convert items to rest object
        if isinstance(items, list):
            rest_items_list = [cls._to_rest_item(item=i) for i in items]
            result = json.dumps(rest_items_list)
        elif isinstance(items, dict):
            rest_items_dict = {k: cls._to_rest_item(item=v) for k, v in items.items()}
            result = json.dumps(rest_items_dict)
        elif isinstance(items, (NodeOutput, PipelineInput)):
            result = str(items)
        elif isinstance(items, str):
            result = items
        else:
            raise UserErrorException("Unsupported items type: {}".format(type(items)))
        return result

    def _to_rest_object(self, **kwargs: Any) -> dict:  # pylint: disable=unused-argument
        """Convert self to a rest object for remote call.

        :return: The rest object
        :rtype: dict
        """
        rest_node = super(ParallelFor, self)._to_rest_object(**kwargs)
        # convert items to rest object
        rest_items = self._to_rest_items(items=self.items)
        rest_node.update({"items": rest_items, "outputs": self._to_rest_outputs()})
        # TODO: Bug Item number: 2897665
        res: dict = convert_ordered_dict_to_dict(rest_node)  # type: ignore
        return res

    @classmethod
    # pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
    def _from_rest_item(cls, rest_item: Any) -> Dict:
        """Convert rest item to item."""
        primitive_inputs, asset_inputs = {}, {}
        for key, val in rest_item.items():
            if isinstance(val, dict) and val.get("job_input_type"):
                asset_inputs[key] = val
            else:
                primitive_inputs[key] = val
        return {**cls._from_rest_inputs(inputs=asset_inputs), **primitive_inputs}

    @classmethod
    # pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
    def _from_rest_items(cls, rest_items: str) -> Union[dict, list, str]:
        """Convert items from rest object."""
        try:
            items = json.loads(rest_items)
        except json.JSONDecodeError:
            # return original items when failed to load
            return rest_items
        if isinstance(items, list):
            return [cls._from_rest_item(rest_item=i) for i in items]
        if isinstance(items, dict):
            return {k: cls._from_rest_item(rest_item=v) for k, v in items.items()}
        return rest_items

    @classmethod
    def _from_rest_object(cls, obj: dict, pipeline_jobs: dict) -> "ParallelFor":
        # pylint: disable=protected-access
        obj = BaseNode._from_rest_object_to_init_params(obj)
        obj["items"] = cls._from_rest_items(rest_items=obj.get("items", ""))
        return cls._create_instance_from_schema_dict(pipeline_jobs=pipeline_jobs, loaded_data=obj)

    @classmethod
    def _create_instance_from_schema_dict(cls, pipeline_jobs: Dict, loaded_data: Dict, **kwargs: Any) -> "ParallelFor":
        body_name = cls._get_data_binding_expression_value(loaded_data.pop("body"), regex=r"\{\{.*\.jobs\.(.*)\}\}")

        loaded_data["body"] = cls._get_body_from_pipeline_jobs(pipeline_jobs=pipeline_jobs, body_name=body_name)
        return cls(**loaded_data, **kwargs)

    def _convert_output_meta(self, outputs: Dict[str, Union[NodeOutput, Output]]) -> Dict[str, Output]:
        """Convert output meta to aggregate types.

        :param outputs: Output meta
        :type outputs: Dict[str, Union[NodeOutput, Output]]
        :return: Dictionary of aggregate types
        :rtype: Dict[str, Output]
        """
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
                output = output._to_job_output()  # type: ignore
            if isinstance(output, Output):
                out_dict = output._to_dict()
                out_dict["type"] = new_type
                resolved_output = Output(**out_dict)
            else:
                resolved_output = Output(type=new_type)
            aggregate_outputs[name] = resolved_output
        return aggregate_outputs

    def _customized_validate(self) -> MutableValidationResult:
        """Customized validation for parallel for node.

        :return: The validation result
        :rtype: MutableValidationResult
        """
        # pylint: disable=protected-access
        validation_result = self._validate_body()
        validation_result.merge_with(
            self._validate_items(items=self.items, raise_error=False, body_component=self.body._component)
        )
        return validation_result

    @classmethod
    def _validate_items(
        cls,
        items: Union[list, dict, str, NodeOutput, PipelineInput],
        raise_error: bool = True,
        body_component: Optional[Union[str, Component]] = None,
    ) -> MutableValidationResult:
        validation_result = cls._create_empty_validation_result()
        if items is not None:
            if isinstance(items, str):
                # TODO: remove the validation
                # try to deserialize str if it's a json string
                try:
                    items = json.loads(items)
                except json.JSONDecodeError as e:
                    if not is_data_binding_expression(items, ["parent"]):
                        validation_result.append_error(
                            yaml_path="items",
                            message=f"Items is neither a valid JSON string due to {e} or a binding string.",
                        )
            if isinstance(items, dict):
                # Validate dict keys
                items = list(items.values())
            if isinstance(items, list):
                if len(items) > 0:
                    cls._validate_items_list(items, validation_result, body_component=body_component)
                else:
                    validation_result.append_error(yaml_path="items", message="Items is an empty list/dict.")
        else:
            validation_result.append_error(
                yaml_path="items",
                message="Items is required for parallel_for node",
            )
        return cls._try_raise(validation_result, raise_error=raise_error)

    @classmethod
    def _validate_items_list(
        cls,
        items: list,
        validation_result: MutableValidationResult,
        body_component: Optional[Union[str, Component]] = None,
    ) -> None:
        # pylint: disable=protected-access
        meta: dict = {}
        # all items have to be dict and have matched meta
        for item in items:
            # item has to be dict
            # Note: item can be empty dict when loop_body don't have foreach inputs.
            if not isinstance(item, dict):
                validation_result.append_error(
                    yaml_path="items",
                    message=f"Items has to be list/dict of dict as value, " f"but got {type(item)} for {item}.",
                )
            else:
                # item has to have matched meta
                if meta.keys() != item.keys():
                    if not meta.keys():
                        meta = item
                    else:
                        msg = f"Items should have same keys with body inputs, but got {item.keys()} and {meta.keys()}."
                        validation_result.append_error(yaml_path="items", message=msg)
                # items' keys should appear in body's inputs
                if isinstance(body_component, Component) and (not item.keys() <= body_component.inputs.keys()):
                    msg = f"Item {item} got unmatched inputs with loop body component inputs {body_component.inputs}."
                    validation_result.append_error(yaml_path="items", message=msg)
                # validate item value type
                cls._validate_item_value_type(item=item, validation_result=validation_result)

    @classmethod
    def _validate_item_value_type(cls, item: dict, validation_result: MutableValidationResult) -> None:
        # pylint: disable=protected-access
        supported_types = (Input, str, bool, int, float, PipelineInput)
        for _, val in item.items():
            if not isinstance(val, supported_types):
                validation_result.append_error(
                    yaml_path="items",
                    message="Unsupported type {} in parallel_for items. Supported types are: {}".format(
                        type(val), supported_types
                    ),
                )
            if isinstance(val, Input):
                cls._validate_input_item_value(entry=val, validation_result=validation_result)

    @classmethod
    def _validate_input_item_value(cls, entry: Input, validation_result: MutableValidationResult) -> None:
        if not isinstance(entry, Input):
            return
        if not entry.path:
            validation_result.append_error(
                yaml_path="items",
                message=f"Input path not provided for {entry}.",
            )
        if isinstance(entry.path, str) and os.path.exists(entry.path):
            validation_result.append_error(
                yaml_path="items",
                message=f"Local file input {entry} is not supported, please create it as a dataset.",
            )
