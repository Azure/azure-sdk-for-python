# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union, List

from azure.ai.ml import Output
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.control_flow_job import FLScatterGatherSchema
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.constants._common import FL_SILO_MERGE_OUTPUT
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, validate_attribute_type
from azure.ai.ml.constants import JobType

from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._assets._artifacts.model import Model
from azure.ai.ml.entities._builders.fl_test_builders import merge_comp

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
    : TODO validate that each silo's compute is allowed to l ook at data from the specified input location
    """

    def __init__(
        self,
        *,
        silo_configs: List[FederatedLearningSilo],
        silo_component: Component,
        aggregation_component: Component,
        shared_silo_kwargs: Dict = {},
        aggregation_config: FederatedLearningSilo = None,
        aggregation_kwargs: Dict = {},
        silo_to_aggregation_argument_map: Dict = {},
        aggregation_to_silo_argument_map: Dict = {},
        max_iterations: int = 1,
        pass_iteration_to_copmonents: bool = False,
        pass_index_to_silo_copmonents: bool = False,
        **kwargs,
    ):

        self._init = True
        self.silo_configs = silo_configs
        self.aggregation_config = aggregation_config
        self.silo_component = silo_component
        self.aggregation_component = aggregation_component
        self.shared_silo_kwargs = shared_silo_kwargs
        self.aggregation_kwargs = aggregation_kwargs
        self.silo_to_aggregation_argument_map = silo_to_aggregation_argument_map
        self.aggregation_to_silo_argument_map = aggregation_to_silo_argument_map
        self.max_iterations = max_iterations
        self._validate_inputs()

        executed_aggregation_component = None
       
        for i in range(self.max_iterations):
            silo_inputs = {}
            # Create inputs for silo components by merging last iteration's aggregation ouput into the standard,
            # user-provided input
            silo_inputs.update(self.shared_silo_kwargs)
            if executed_aggregation_component is not None and self.silo_to_aggregation_argument_map is not None:
                silo_inputs.update(FLScatterGather._extract_outputs(executed_aggregation_component.outputs, self.aggregation_to_silo_argument_map))

            executed_aggregation_component = self.scatter_gather(silo_inputs, i)
        # TODO figure out final ouputs (might want another user input)
        #self._outputs = self._construct_outputs(executed_aggregation_component)
        # TODO somehow annotate this node so that it's easy to ID as an fl job
        #super(FLScatterGather, self).__init__()
        super(FLScatterGather, self).__init__(
            type=JobType.COMPONENT,  # pylint: disable=redefined-builtin
            component=None,
            inputs= None,
            outputs= None,
            name= None,
            display_name= None,
            description= None,
            tags= None,
            properties= None,
            comment= None,
            compute= None,
            experiment_name= None,
        )


    # TODO potential set default fail_on_missing value to false
    @classmethod
    def _extract_outputs(cls, component_output: Output, argument_map: Dict, fail_on_missing=False):
        """
            Pulls values from a component_output, as specified by the keys of the
        inputted argument_map, and groups in a new dictionary. The keys of the new dictionary
        are specified by the items of the argument_map dictionary.

        Example
            component_output = {"one" : 1, "two": 2, "three" : 3}
            argument_map = {"one" : "red", "two" : "two"}
            returned result = {"red" : 1, "two" : 2}
        """
        result = {}
        if component_output is None or argument_map is None:
            if fail_on_missing:
                # TODO error handling
                pass
            return result
        
        for k, v in argument_map.items():
            if not k in component_output:
                if fail_on_missing:
                    pass
                    # TODO add error handling
                result[v] = None
            else:
                result[v] = component_output[k]
        return result

    # TODO rearrange functions to be less of a disorganized eyesore
    def scatter_gather(self, silo_inputs : Dict, index : int):
        '''
            Performs a scatter-gather iteration by running copies of the silo component on different
        computes/datstores according to the node's inputted silo configs. The outputs of these
        silo components are then merged by an internal helper component. The single, merged value
        is then inputted into the user-provided aggregation component. Returns the executed aggregation component.
        '''

        outputs = {}
        for i in range(len(self.silo_configs)):
            silo_config = self.silo_configs[i]
            # TODO input modified shared_silo_kwargs to include updated model and such
            executed_silo_component = self.silo_component(**silo_inputs)
            FLScatterGather._apply_siloing_to_executed_component(component=executed_silo_component, silo=silo_config)
            # TODO Make use of this function instead
            #FLScatterGather._anchor_step_in_silo(pipeline_step=executed_silo_component, compute=silo_config.compute, output_datastore=silo_config.datastore)
            # TODO Make sure of silo_to_aggregation_argument_map to selectively extract outputs
            # in merge component

            # Extract user-specified outputs from the silo component, rename them as needed, annotate them with the silo's index, then jam them all into the
            # variable-length internal component's input list. 
            #siloed_outputs.update({"{}_{}".format(k,i) : v for k,v in FLScatterGather._extract_outputs(executed_silo_component.outputs, self.silo_to_aggregation_argument_map).items()})
            outputs["input_{}".format(i)] = executed_silo_component.outputs["silo_output"]

        executed_merge_component = merge_comp(**outputs, index=i)
        test = merge_comp(index2=i)
        import pdb; pdb.set_trace()
        # TODO continue to make use of silo_to_aggregation_argument_map to send outputs form
        # merge comp to aggregation_comp
        # TODO input modified aggregation_kwargs that includes merge_comp outputs
        agg_inputs = {}
        agg_inputs.update(self.aggregation_kwargs)
        # agg_inputs.update(executed_merge_component.outputs)
        executed_aggregation_component = self.aggregation_component(**agg_inputs)

        if self.aggregation_config is not None:
            # internal merge component is also siloed to wherever the aggregation component lives.
            # FLScatterGather._apply_siloing_to_executed_component(executed_merge_component, self.aggregation_config)
            FLScatterGather._apply_siloing_to_executed_component(executed_aggregation_component, self.aggregation_config)
            # TODO make use of these functions instead of unrecursive compute datastore/compute setting
            #FLScatterGather._anchor_step_in_silo(pipeline_step=executed_merge_component, compute=self.aggregation_config.compute, output_datastore=self.aggregation_config.datastore)
            #FLScatterGather._anchor_step_in_silo(pipeline_step=executed_aggregation_component, compute=self.aggregation_config.compute, output_datastore=self.aggregation_config.datastore)

        return executed_aggregation_component

    @classmethod
    def custom_fl_data_output(
        cls, datastore_name, output_name, unique_id="${{name}}", iteration_num=None
    ):
        """Returns an Output pointing to a path to store the data during FL training.
        Args:
            datastore_name (str): name of the Azure ML datastore
            output_name (str): a name unique to this output
            unique_id (str): a unique id for the run (default: inject run id with ${{name}})
            iteration_num (str): an iteration number if relevant
        Returns:
            data_path (str): direct url to the data path to store the data
        """
        data_path = f"azureml://datastores/{datastore_name}/paths/federated_learning/{output_name}/{unique_id}/"
        if iteration_num:
            data_path += f"iteration_{iteration_num}/"

        return Output(type=AssetTypes.URI_FOLDER, mode="mount", path=data_path)

    # TODO Get this to work tentative simplified datastore override was failing), and make sure it's very robust
    @classmethod
    def _anchor_step_in_silo(
        cls,
        pipeline_step,
        compute,
        output_datastore,
        tags={},
        description=None,
        _path="root",
    ):
        """Take a step and recursively enforce the right compute/datastore config.
        Args:
            pipeline_step (PipelineStep): a step to anchor
            compute (str): name of the compute target
            output_datastore (str): name of the datastore for the outputs of this step
            tags (dict): tags to add to the step in AzureML UI
            description (str): description of the step in AzureML UI
            _path (str): for recursive anchoring, codes the "path" inside the pipeline
        Returns:
            pipeline_step (PipelineStep): the anchored step
        """
        # TODO re-enable logging
        #self.logger.debug(f"{_path}: anchoring node of type={pipeline_step.type}")

        if pipeline_step.type == "pipeline":  # if the current step is a pipeline
            if hasattr(pipeline_step, "component"):
                # current step is a pipeline component
                #self.logger.debug(f"{_path} --  pipeline component detected")

                # then anchor the component inside the current step
                cls.anchor_step_in_silo(
                    pipeline_step.component,
                    compute,
                    output_datastore,
                    tags=tags,
                    description=description,
                    _path=f"{_path}.component",  # pass the path for the debug logs
                )

                # and make sure every output data is anchored to the right datastore
                for key in pipeline_step.outputs:
                    #self.logger.debug(f"{_path}.outputs.{key}: has type={pipeline_step.outputs[key].type} class={type(pipeline_step.outputs[key])}, anchoring to datastore={output_datastore}")
                    setattr(
                        pipeline_step.outputs,
                        key,
                        self.custom_fl_data_output(output_datastore, key),
                    )

            else:
                # current step is a (regular) pipeline (likely the root of the graph)
                #self.logger.debug(f"{_path}: pipeline (regular) detected")

                # let's anchor each outputs of the pipeline to the right datastore
                for key in pipeline_step.outputs:
                    #self.logger.debug(f"{_path}.outputs.{key}: has type={pipeline_step.outputs[key].type} class={type(pipeline_step.outputs[key])}, anchoring to datastore={output_datastore}")
                    pipeline_step.outputs[key] = self.custom_fl_data_output(
                        self.orchestrator["datastore"], key
                    )

                # then recursively anchor each job inside the pipeline
                for job_key in pipeline_step.jobs:
                    job = pipeline_step.jobs[job_key]
                    cls.anchor_step_in_silo(
                        job,
                        compute,
                        output_datastore,
                        tags=tags,
                        description=description,
                        _path=f"{_path}.jobs.{job_key}",  # pass the path for the debug logs
                    )

            # return the anchored pipeline
            return pipeline_step

        elif pipeline_step.type == "command":
            # if the current step is a command
            #self.logger.debug(f"{_path}: command detected")

            # make sure the compute corresponds to the silo
            if pipeline_step.compute is None:
                #self.logger.debug(f"{_path}: compute is None, forcing compute={compute} instead")
                pipeline_step.compute = compute

            # then anchor each of the job's outputs to the right datastore
            for key in pipeline_step.outputs:
                #self.logger.debug(f"{_path}.outputs.{key}: has type={pipeline_step.outputs[key].type} class={type(pipeline_step.outputs[key])}, anchoring to datastore={output_datastore}")

                if pipeline_step.outputs[key]._data is None:
                    # if the output is an intermediary output
                    #self.logger.debug(f"{_path}.outputs.{key}: intermediary output detected, forcing datastore {output_datastore}")
                    setattr(
                        pipeline_step.outputs,
                        key,
                        self.custom_fl_data_output(output_datastore, key),
                    )
                else:
                    pass
                    # if the output is an internal reference to a parent output
                    # let's trust that the parent has been anchored properly
                    #self.logger.debug(f"{_path}.outputs.{key}: reference ouptut detected, leaving as is")

            # return the anchored pipeline
            return pipeline_step

        else:
            # TODO revisit this
            raise NotImplementedError(f"under path={_path}: step type={pipeline_step.type} is not supported")


    @classmethod
    def _apply_siloing_to_executed_component(cls, component: Component, silo: FederatedLearningSilo):
        """
            Modifies an executed (aka __call__'ed) component to run on the compute and datastore
        specified by the inputted silo. The 'input' value of the silo is not considered.
        """

        component.compute = silo.compute
        comment = '''for key in component.outputs:
            #self.logger.debug(f"{_path}.outputs.{key}: has type={pipeline_step.outputs[key].type} class={type(pipeline_step.outputs[key])}, anchoring to datastore={output_datastore}")

            if component.outputs[key]._data is None:
                # if the output is an intermediary output
                #self.logger.debug(f"{_path}.outputs.{key}: intermediary output detected, forcing datastore {output_datastore}")
                setattr(
                    component.outputs,
                    key,
                    cls.custom_fl_data_output(component, key),
                )'''


    def _construct_silo_input_from_aggregation(executed_aggregation_component):
        """
            Produces the inputs for the next scatter-gather inputs' silo components from the previous
            iterations executed aggregation component, using the inputted aggregation_to_silo_argument_map
            to determine how to map values around.
        """
        # Actually do what's said on the tin
        return executed_aggregation_component.outputs


    def _construct_final_output(executed_aggregation_component):
        """
            Produces the outputs of the overall node based on the the final aggregation component.
        """
        # TODO probably make this vary based on user mappings
        # might need an agg-to-output map or an agg-to-silo map
        return executed_aggregation_component.outputs

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

    @ classmethod
    def _custom_fl_data_path(datastore_name, output_name, unique_id="${{name}}", iteration_num="${{iteration_num}}"):
        """Produces a path to store the data during FL training.
        Args:
            datastore_name (str): name of the Azure ML datastore
            output_name (str): a name unique to this output
            unique_id (str): a unique id for the run (default: inject run id with ${{name}})
            iteration_num (str): an iteration number if relevant
        Returns:
            data_path (str): direct url to the data path to store the data
        """
        data_path = f"azureml://datastores/{datastore_name}/paths/federated_learning/{output_name}/{unique_id}/"
        if iteration_num is not None:
            data_path += f"iteration_{iteration_num}/"

        return data_path

