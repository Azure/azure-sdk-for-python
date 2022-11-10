# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union

from azure.ai.ml import Output
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.control_flow_job import ParallelForSchema
from azure.ai.ml.constants._component import ControlFlowType
from azure.ai.ml.entities._builders.control_flow_node import LoopNode
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin
from azure.ai.ml.entities._util import validate_attribute_type


class ParallelFor(LoopNode, NodeIOMixin):
    """Parallel for loop node in the pipeline job.
    By specifying the loop body and aggregated items, a job-level parallel for loop can be implemented.
    It will be initialized when calling dsl.parallel_for or when loading the pipeline yml containing parallel_for node.
    Please do not manually initialize this class.

    :param body: Pipeline job for the parallel for loop body.
    :type body: Pipeline
    :param items: The loop body's input which will bind to the loop node
    :type items: Union[list, dict]
    :param max_concurrency: Maximum number of concurrent iterations to run. All loop body nodes will be executed
        in parallel if not specified.
    :type max_concurrency: int
    """

    def __init__(
            self,
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
        # parallel for node shares output meta with body
        # TODO: handle when body don't have component or outputs
        outputs = self.body._component.outputs
        self._outputs = self._build_outputs_dict_without_meta(outputs or {})

        self.items = items

    @property
    def outputs(self) -> Dict[str, Union[str, Output]]:
        return self._outputs

    @classmethod
    def _create_schema_for_validation(cls, context) -> PathAwareSchema:
        return ParallelForSchema(context=context)

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "items": (dict, list),
        }

    def _to_rest_object(self, **kwargs) -> dict:  # pylint: disable=unused-argument
        """Convert self to a rest object for remote call."""
        rest_node = super(ParallelFor, self)._to_rest_object(**kwargs)
        if rest_node.get("items"):
            # serialize items to string
            rest_node["items"] = json.dumps(rest_node["items"])
        return rest_node

    def _customized_validate(self):
        """Customized validation for parallel for node."""
        validation_result = self._validate_body(raise_error=False)
        return validation_result
