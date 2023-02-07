# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union, List

from azure.ai.ml import Output
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.control_flow_job import FLScatterGatherSchema
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, validate_attribute_type

from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._assets._artifacts.model import Model

# TODO: Determine if this should inherit ControlFlowNode, LoopNode, BaseNode, or something else.
# Argument in favor of BaseNode - this Node DOES have I/O, unlike CFNode apparently.
# Arg against BaseNode: BaseNode does some strict processing on I/O, which this node might not want to deal with
# Arg against ContorlFlowNode and LoopNode: No I/O, it's inherent to the inputted body (I think)
# I ultimately chose BaseNode because I think we'll want the I/O process that BaseNode does, even
# if it hampers us a bit at first. Also, I definitely don't consider this a subtype of a LoopNode,
# and I'm not sure if it really counts as a subtype of ControlFlowNode.
class FLScatterGather(BaseNode, NodeIOMixin): 
    """A node which creates a federated learning scatter-gather loop as a pipeline subgraph.
    Intended for use inside a pipeline job. This is initialized when calling
    dsl.fl_scatter_gather() or when loading a serialized version of this node from YAML.
    Please do not manually initialize this class.

    : TODO Param types
    """

    def __init__(
        self,
        *,
        silo_configs: List[FederatedLearningSilo],
        silo_component: PipelineComponent,
        shared_silo_kwargs: Dict,
        aggregation_config: Dict,
        aggregation_component: PipelineComponent,
        aggregation_kwargs: Dict,
        silo_to_aggregation_argument_map: Dict,
        max_iterations: int,
        **kwargs,
    ):
        # ... set inputs
        self._validate_inputs()

        # BIG TODO - maniuplate inputs into a subgraph based on Ankit's work.
        

        super(FLScatterGather, self).__init__(
            # Todo, parent node inputs will probably depend on values produced
            # by big todo above.
        )

    @property
    def outputs(self) -> Dict[str, Union[str, Output]]:
        # TODO - assign _outputs based on either new input or derivation of subgraph.
        return self._outputs

    @classmethod
    def _create_schema_for_validation(cls, context) -> PathAwareSchema:
        return FLScatterGatherSchema(context=context)

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            **super(FLScatterGather, cls)._attr_type_map(),
            "items": (dict, list, str, PipelineInput, NodeOutput),
        }

    def _to_rest_object(self, **kwargs) -> dict:  # pylint: disable=unused-argument
        """Convert self to a rest object for remote call."""
        # TODO revisit post-integration
        rest_node = super(FLScatterGather, self)._to_rest_object(**kwargs)
        rest_node.update(dict(outputs=self._to_rest_outputs()))
        return convert_ordered_dict_to_dict(rest_node)

    @classmethod
    def _from_rest_object(cls, obj: dict, pipeline_jobs: dict) -> "FLScatterGather":
        # TODO revisit post-integration
        obj = BaseNode._from_rest_object_to_init_params(obj)
        return cls._create_instance_from_schema_dict(pipeline_jobs=pipeline_jobs, loaded_data=obj)

    @classmethod
    def _create_instance_from_schema_dict(cls, pipeline_jobs, loaded_data):
        # TODO revisit post-integration
        body_name = cls._get_data_binding_expression_value(loaded_data.pop("body"), regex=r"\{\{.*\.jobs\.(.*)\}\}")

        loaded_data["body"] = cls._get_body_from_pipeline_jobs(pipeline_jobs=pipeline_jobs, body_name=body_name)
        return cls(**loaded_data)

    def _convert_output_meta(self, outputs):
        """Convert output meta to aggregate types."""
        # TODO Determine if this is still needed
        pass

    def _validate_inputs(self, raise_error=True):
        pass
        # TODO Implement once input (and especially types) are decided upon
        # TODO 2 - do we want to attempt server-side validation here, like making sure supplied silo configs refer to valid resources, etc?
