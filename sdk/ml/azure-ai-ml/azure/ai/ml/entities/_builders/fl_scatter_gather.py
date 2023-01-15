# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union

from azure.ai.ml import Output
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.control_flow_job import FLScatterGatherSchema
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, validate_attribute_type

# TODO: Determine if this should inherit ControlFlowNode, LoopNode, or neither.
class FLScatterGather(ControlFlowNode, NodeIOMixin): 
    """A node which creates a federated learning scatter-gather loop as a pipeline subgraph.
    Intended for use inside a pipeline job. This is initialized when calling
    dsl.fl_scatter_gather() or when loading a serialized version of this node from YAML.
    Please do not manually initialize this class.

    : TODO Param types
    """

    def __init__(
        self,
        *,
        model, # TODO determine typehint of this
        silo_configs, # TODO determine (and probably create) typehint of this
        learning_func, # TODO determine typehint of this
        aggregation_func, # TODO determine typehint of this
        max_iterations: int,
        #max_concurrency=None # TODO should this still be a value?
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs.pop("type", None)
        super(FLScatterGather, self).__init__(
            type=NodeType.FL_SCATTER_GATHER,
            body=None,
            **kwargs,
        )
        # Todo, possibly catch errors thrown by this
        self.validate_inputs(model, silo_configs, learning_func, aggregation_func, max_iterations)
        # Pseudo code of the hardest part of this POC, the actual scatter-gather subgraph creation.
        # The below is a high-level idea of the behavior that we want to have run in Azure when 
        # this node is submitted. How that's actually achieved is still something I don't understand,
        # since I've yet to find the code that seems to correlate nodes to server-side orchestration.
        '''
        for i in range(0, max_iterations):
            silo_comps = []
            for silo_config in silo_configs:
                silo_comps.add(create_silo_component(silo_config, learning_func))
            agg_comp = create_aggregate_component([silo.output for silo in silo_comps], aggregate_func)
            if learning_thresholds_reached(agg_comp.output, input_model):
                break
        
        '''



    @property
    def outputs(self) -> Dict[str, Union[str, Output]]:
        # TODO Validate
        return self._outputs

    @classmethod
    def _create_schema_for_validation(cls, context) -> PathAwareSchema:
        # TODO Validate
        return FLScatterGatherSchema(context=context)

    @classmethod
    def _attr_type_map(cls) -> dict:
        # TODO Validate
        return {
            **super(FLScatterGather, cls)._attr_type_map(),
            "items": (dict, list, str, PipelineInput, NodeOutput),
        }

    def _to_rest_object(self, **kwargs) -> dict:  # pylint: disable=unused-argument
        """Convert self to a rest object for remote call."""
        # TODO Validate
        rest_node = super(FLScatterGather, self)._to_rest_object(**kwargs)
        rest_node.update(dict(outputs=self._to_rest_outputs()))
        return convert_ordered_dict_to_dict(rest_node)

    @classmethod
    def _from_rest_object(cls, obj: dict, pipeline_jobs: dict) -> "FLScatterGather":
        # TODO Validate
        obj = BaseNode._from_rest_object_to_init_params(obj)
        return cls._create_instance_from_schema_dict(pipeline_jobs=pipeline_jobs, loaded_data=obj)

    @classmethod
    def _create_instance_from_schema_dict(cls, pipeline_jobs, loaded_data):
        # TODO Validate
        body_name = cls._get_data_binding_expression_value(loaded_data.pop("body"), regex=r"\{\{.*\.jobs\.(.*)\}\}")

        loaded_data["body"] = cls._get_body_from_pipeline_jobs(pipeline_jobs=pipeline_jobs, body_name=body_name)
        return cls(**loaded_data)

    def _convert_output_meta(self, outputs):
        """Convert output meta to aggregate types."""
        # TODO Determine if this is still needed
        pass

    def _validate_inputs(self, raise_error=True):
        pass
        # TODO Implement once inputs are decided upon
