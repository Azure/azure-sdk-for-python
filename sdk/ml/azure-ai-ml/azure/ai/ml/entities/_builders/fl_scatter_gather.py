# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Union, List, Optional
import re

from azure.ai.ml import Output
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.control_flow_job import FLScatterGatherSchema
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict
from azure.ai.ml.constants import JobType

from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._validation import MutableValidationResult
from azure.ai.ml.dsl._do_while import do_while
from azure.ai.ml.dsl import pipeline
from .subcomponents import create_scatter_output_table


# TODO 2293610: add support for more types of outputs besides uri_folder and mltable
# Likely types that ought to be mergeable: string, int, uri_file
MERGE_COMPONENT_MAPPING = {
    "mltable": create_scatter_output_table,
    "uri_folder": create_scatter_output_table,
}


ANCHORABLE_OUTPUT_TYPES = {AssetTypes.MLTABLE, AssetTypes.URI_FOLDER}

ANCHORING_PATH_ROOT = "root"


# big TODO: For some reason, surfacing this file in  __init__.py causes
#  a circular import exception on the first attempted import
# In notebooks, the second import succeeds, but then causes a silent failure where the
# MLDesigner component created by the subcomponents.create_scatter_output_table function
# will produce a ComponentExecutor object instead of the actual component.
# TODO 2293541: Add telemetry of some sort
# pylint: disable=too-many-instance-attributes
class FLScatterGather(ControlFlowNode, NodeIOMixin):
    """A node which creates a federated learning scatter-gather loop as a pipeline subgraph.
    Intended for use inside a pipeline job. This is initialized when calling
    dsl.fl_scatter_gather() or when loading a serialized version of this node from YAML.
    Please do not manually initialize this class.
    """

    # See node class for input descriptions, no point maintaining
    # double descriptions between a wrapper its interior.
    def __init__(
        self,
        *,
        silo_configs: List[FederatedLearningSilo],
        silo_component: Component,
        aggregation_component: Component,
        aggregation_compute: str = None,
        aggregation_datastore: str = None,
        shared_silo_kwargs: Optional[Dict] = None,
        aggregation_kwargs: Optional[Dict] = None,
        silo_to_aggregation_argument_map: Optional[Dict] = None,
        aggregation_to_silo_argument_map: Optional[Dict] = None,
        max_iterations: int = 1,
        create_default_mappings_if_needed: bool = False,
        **kwargs,
    ):
        # auto-create X_to_Y_argument_map values if allowed and needed.
        if create_default_mappings_if_needed:
            # pylint: disable=line-too-long
            (
                silo_to_aggregation_argument_map,
                aggregation_to_silo_argument_map,
            ) = FLScatterGather._try_create_default_mappings(
                silo_component,
                aggregation_component,
                silo_to_aggregation_argument_map,
                aggregation_to_silo_argument_map,
            )

        # input validation.
        FLScatterGather.validate_inputs(
            silo_configs=silo_configs,
            silo_component=silo_component,
            aggregation_component=aggregation_component,
            shared_silo_kwargs=shared_silo_kwargs,
            aggregation_compute=aggregation_compute,
            aggregation_datastore=aggregation_datastore,
            aggregation_kwargs=aggregation_kwargs,
            silo_to_aggregation_argument_map=silo_to_aggregation_argument_map,
            aggregation_to_silo_argument_map=aggregation_to_silo_argument_map,
            max_iterations=max_iterations,
        )

        # store inputs
        self.silo_configs = silo_configs
        self.aggregation_compute = aggregation_compute
        self.aggregation_datastore = aggregation_datastore
        self.silo_component = silo_component
        self.aggregation_component = aggregation_component
        self.shared_silo_kwargs = shared_silo_kwargs
        self.aggregation_kwargs = aggregation_kwargs
        self.silo_to_aggregation_argument_map = silo_to_aggregation_argument_map
        self.aggregation_to_silo_argument_map = aggregation_to_silo_argument_map
        self.max_iterations = max_iterations
        self._init = True  # Needed by parent class to work properly

        self.scatter_gather_graph = self.scatter_gather()

        # set SG node flag for telemetry
        self.scatter_gather_graph.properties["azureml.telemetry.attribution"] = "FederatedLearningSGJobFlag"
        self.scatter_gather_graph._to_rest_object()

        # set output to final aggregation step's output
        self._outputs = self.scatter_gather_graph.outputs
        super(FLScatterGather, self).__init__(
            type=JobType.COMPONENT,  # pylint: disable=redefined-builtin
            component=None,
            inputs=None,
            outputs=self.scatter_gather_graph.outputs,
            name=None,
            display_name=None,
            description=None,
            tags=None,
            properties=None,
            comment=None,
            compute=None,
            experiment_name=None,
        )

    def scatter_gather(self):
        @pipeline(
            name="Scatter gather",
            description="It includes all steps that need to be executed in silo and aggregation",
        )
        def scatter_gather_iteration_body(**silo_inputs):
            """
                Performs a scatter-gather iteration by running copies of the silo step on different
            computes/datstores according to this node's silo configs. The outputs of these
            silo components are then merged by an internal helper component. The merged values
            are then inputted into the user-provided aggregation component. Returns the executed aggregation component.
            Args:
                silo_inputs (dict): A dictionary of names and Inputs to be injected into each executed silo step.
                    This dictionary is merged with silo-specific inputs before each executed.
            """

            silo_outputs = []
            # TODO 2293586 replace this for-loop with a parallel-for node
            for silo_config in self.silo_configs:
                silo_inputs.update(silo_config.inputs)
                executed_silo_component = self.silo_component(**silo_inputs)
                for v, k in executed_silo_component.inputs.items():
                    if v in silo_config.inputs and k.type == "uri_folder":
                        k.mode = "ro_mount"
                FLScatterGather._anchor_step(
                    pipeline_step=executed_silo_component,
                    compute=silo_config.compute,
                    internal_datastore=silo_config.datastore,
                    orchestrator_datastore=self.aggregation_datastore,
                )
                # add to silo outputs list
                silo_outputs.append(executed_silo_component)

            # produce internal argument-merging components and record them in local subgraph
            merge_comp_mapping = self._inject_merge_components(silo_outputs)

            # produce aggregate step inputs by merging static kwargs and mapped arguments from
            # internal merge components
            agg_inputs = {}
            agg_inputs.update(self.aggregation_kwargs)
            internal_merge_outputs = {
                self._get_aggregator_input_name(k): v.outputs.aggregated_output for k, v in merge_comp_mapping.items()
            }
            agg_inputs.update(internal_merge_outputs)

            # run the user aggregation step
            executed_aggregation_component = self.aggregation_component(**agg_inputs)
            # Set mode of aggregated mltable inputs as eval mount to allow files referenced within the table
            # to be accessible by the component
            for name, agg_input in executed_aggregation_component.inputs.items():
                if name in self.silo_to_aggregation_argument_map.values() and agg_input.type == "mltable":
                    agg_input.mode = "eval_download"

            # Anchor both the internal merge components and the user-supplied aggregation step
            # to the aggregation compute and datastore
            if self.aggregation_compute is not None and self.aggregation_datastore is not None:
                # internal merge component is also siloed to wherever the aggregation component lives.
                for executed_merge_component in merge_comp_mapping.values():
                    FLScatterGather._anchor_step(
                        pipeline_step=executed_merge_component,
                        compute=self.aggregation_compute,
                        internal_datastore=self.aggregation_datastore,
                        orchestrator_datastore=self.aggregation_datastore,
                    )
                FLScatterGather._anchor_step(
                    pipeline_step=executed_aggregation_component,
                    compute=self.aggregation_compute,
                    internal_datastore=self.aggregation_datastore,
                    orchestrator_datastore=self.aggregation_datastore,
                )
            return executed_aggregation_component.outputs

        @pipeline(name="Scatter gather graph")
        def create_scatter_gather_graph():
            """
            Creates a scatter-gather graph by executing the scatter_gather_iteration_body
            function in a do-while loop. The loop terminates when the user-supplied
            termination condition is met.
            """

            silo_inputs = {}
            # Start with static inputs
            silo_inputs.update(self.shared_silo_kwargs)

            # merge in inputs passed in from previous iteration's aggregate step)
            if self.aggregation_to_silo_argument_map is not None:
                silo_inputs.update({v: None for v in self.aggregation_to_silo_argument_map.values()})

            scatter_gather_body = scatter_gather_iteration_body(**silo_inputs)

            # map aggregation outputs to scatter inputs
            do_while_mapping = {
                k: getattr(scatter_gather_body.inputs, v) for k, v in self.aggregation_to_silo_argument_map.items()
            }

            do_while(
                body=scatter_gather_body,
                mapping=do_while_mapping,
                max_iteration_count=self.max_iterations,
            )
            return scatter_gather_body.outputs

        return create_scatter_gather_graph()

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

    @classmethod
    def _get_fl_datastore_path(
        cls,
        datastore_name: str,
        output_name: str,
        unique_id: str = "${{name}}",
        iteration_num: Optional[int] = None,
    ) -> str:
        """Construct a path string using the inputted values. The important aspect is that this produces a
        path with a specified datastore.

        Args:
            datastore_name (str): The datastore to use in the constructed path.
            output_name (str): The name of the output value that this path is assumed to belong to. Is injected into
                the path.
            unique_id (str): An additional string to inject if needed.
                Defaults to ${{name}}, which is the output name again.
            iteration_num: optional[int]: The iteration number of the current scatter-gather iteration.
                If set, inject this into the resulting path string.

        Returns:
            data_path: A data path string containing the various aforementioned inputs.

        """
        data_path = f"azureml://datastores/{datastore_name}/paths/federated_learning/{output_name}/{unique_id}/"
        if iteration_num:
            data_path += f"iteration_{iteration_num}/"
        return data_path

    @classmethod
    def _check_datastore(cls, path: str, expected_datastore: str) -> bool:
        """Perform a simple regex check to try determine if the datastore in the inputted path string
        matches the expected_datastore.

        Args:
            path (str): An output pathstring.
            expected_datastore (str): A datastore name.
        Returns:
            nameless bool: Whether or not the expected_datastore was found in the path at the expected location.
        """
        match = re.match("(.*datastore/)([^/]*)(/.*)", path)
        if match:
            groups = match.groups()
            if groups[1] == expected_datastore:
                return True
        return False

    @classmethod
    def _check_or_set_datastore(
        cls,
        name: str,
        output: Output,
        target_datastore: str,
        iteration_num: Optional[int] = None,
    ) -> MutableValidationResult:
        """Tries to assign output.path to a value which includes the target_datastore if it's not already
        set. If the output's path is already set, return a warning if it doesn't match the target_datastore.

        Args:
            name (str): The name of the output to modify
            output (Output): The output object to examine and potentially change the datastore of.
            target_datastore (str): The name of the datastore to try applying to the output
            iteration_num (optional[int]): the current iteration in the scatter gather loop.
                If set, include this in the generated path.
        Returns:
            validation_result (MutableValidationResult): A validation result containing any problems that arose.
            Contains a warning if the examined output already contains a datastore that does not match
            'target_datastore'.
        """
        validation_result = cls._create_empty_validation_result()
        if not hasattr(output, "path") or not output.path:
            output.path = cls._get_fl_datastore_path(target_datastore, name, iteration_num=iteration_num)
        # Double check the path's datastore leads to the target if it's already set.
        elif not cls._check_datastore(output.path, target_datastore):
            validation_result.append_warning(
                yaml_path=name,
                message=f"Output '{name}' has an undetermined datastore, or a datstore"
                + f" that does not match the expected datastore for this output, which is '{target_datastore}'."
                + " Make sure this is intended.",
            )
        return validation_result

    # TODO 2293705: Add anchoring for more resource types.
    @classmethod
    def _anchor_step(
        cls,
        pipeline_step,
        compute,
        internal_datastore,
        orchestrator_datastore,
        iteration: Optional[int] = 0,
        _path="root",
    ) -> MutableValidationResult:
        """Take a pipeline step and recursively enforces the right compute/datastore config.
        Args:
            pipeline_step (PipelineStep, CommandComponent): a step to anchor
            compute (str): name of the compute target
            internal_datastore (str): The name of the datastore that should be used for internal
                output anchoring.
            orchestrator_datastore (str): The name of the orchestrator/aggregation datastore that
                should be used for 'real' output anchoring.
            _path (str): for recursive anchoring, codes the "path" inside the pipeline for messaging
        Returns:
            validation_result (MutableValidationResult): A validation result containing any issues
                that were uncovered during anchoring. This function adds warnings when outputs already have
                assigned paths which don't contain the expected datastore.
        """

        validation_result = cls._create_empty_validation_result()

        # Current step is a pipeline, which means we need to inspect its steps (jobs) and
        # potentially anchor those as well.
        if pipeline_step.type == "pipeline":
            if hasattr(pipeline_step, "component"):
                # Current step is probably not the root of the graph
                # its outputs should be anchored to the internal_datastore.
                for name, output in pipeline_step.outputs.items():
                    if output.type in ANCHORABLE_OUTPUT_TYPES:
                        validation_result.merge_with(
                            cls._check_or_set_datastore(
                                name=name,
                                output=output,
                                target_datastore=orchestrator_datastore,
                                iteration_num=iteration,
                            )
                        )

                # then we need to anchor the internal component of this step
                # The outputs of this sub-component are a deep copy of the outputs of this step
                # This is dangerous, and we need to make sure they both use the same datastore,
                # so we keep datastore types identical across this recursive call.
                cls._anchor_step(
                    pipeline_step.component,
                    compute,
                    internal_datastore=internal_datastore,
                    orchestrator_datastore=orchestrator_datastore,
                    _path=f"{_path}.component",
                )

            else:
                # This is a pipeline step with multiple jobs beneath it.
                # Anchor its outputs...
                for name, output in pipeline_step.outputs.items():
                    if output.type in ANCHORABLE_OUTPUT_TYPES:
                        validation_result.merge_with(
                            cls._check_or_set_datastore(
                                name=name,
                                output=output,
                                target_datastore=orchestrator_datastore,
                                iteration_num=iteration,
                            )
                        )
                # ...then recursively anchor each job inside the pipeline
                for job_key in pipeline_step.jobs:
                    job = pipeline_step.jobs[job_key]
                    # replace orchestrator with internal datastore, jobs components
                    # should either use the local datastore
                    # or have already had their outputs re-assigned.
                    cls._anchor_step(
                        job,
                        compute,
                        internal_datastore=internal_datastore,
                        orchestrator_datastore=internal_datastore,
                        _path=f"{_path}.jobs.{job_key}",
                    )

        elif pipeline_step.type == "command":
            # if the current step is a command component
            # make sure the compute corresponds to the silo
            if pipeline_step.compute is None:
                pipeline_step.compute = compute
            # then anchor each of the job's outputs
            for name, output in pipeline_step.outputs.items():
                if output.type in ANCHORABLE_OUTPUT_TYPES:
                    validation_result.merge_with(
                        cls._check_or_set_datastore(
                            name=name,
                            output=output,
                            target_datastore=orchestrator_datastore,
                            iteration_num=iteration,
                        )
                    )
        else:
            # TODO revisit this and add support for anchoring more things
            raise NotImplementedError(f"under path={_path}: step type={pipeline_step.type} is not supported")

        return validation_result

    # Making this a class method allows for easier, isolated testing, and allows careful
    # users to call this as a pre-init step.
    # TODO: Might be worth migrating this to a schema validation class, but out of scope for now.
    # pylint: disable=too-many-statements,too-many-branches, too-many-locals
    @classmethod
    def validate_inputs(
        cls,
        *,
        silo_configs: List[FederatedLearningSilo],
        silo_component: Component,
        aggregation_component: Component,
        shared_silo_kwargs: Dict,
        aggregation_compute: str,
        aggregation_datastore: str,
        aggregation_kwargs: Dict,
        silo_to_aggregation_argument_map: Dict,
        aggregation_to_silo_argument_map: Dict,
        max_iterations: int,
        raise_error=False,
    ) -> MutableValidationResult:
        validation_result = cls._create_empty_validation_result()

        # saved values for validation later on
        silo_inputs = None
        silo_outputs = None
        agg_inputs = None
        agg_outputs = None
        # validate silo component
        if silo_component is None:
            validation_result.append_error(
                yaml_path="silo_component",
                message="silo_component is a required argument for the scatter gather node.",
            )
        else:
            # ensure that silo component has both inputs and outputs
            if not hasattr(silo_component, "inputs"):
                validation_result.append_error(
                    yaml_path="silo_component",
                    message="silo_component is missing 'inputs' attribute;"
                    + "it does not appear to be a valid component that can be used in a scatter-gather loop.",
                )
            else:
                silo_inputs = silo_component.inputs
            if not hasattr(silo_component, "outputs"):
                validation_result.append_error(
                    yaml_path="silo_component",
                    message="silo_component is missing 'outputs' attribute;"
                    + "it does not appear to be a valid component that can be used in a scatter-gather loop.",
                )
            else:
                silo_outputs = silo_component.outputs
        # validate aggregation component
        if aggregation_component is None:
            validation_result.append_error(
                yaml_path="aggregation_component",
                message="aggregation_component is a required argument for the scatter gather node.",
            )
        else:
            # ensure that aggregation component has both inputs and outputs
            if not hasattr(aggregation_component, "inputs"):
                validation_result.append_error(
                    yaml_path="aggregation_component",
                    message="aggregation_component is missing 'inputs' attribute;"
                    + "it does not appear to be a valid component that can be used in a scatter-gather loop.",
                )
            else:
                agg_inputs = aggregation_component.inputs
            if not hasattr(aggregation_component, "outputs"):
                validation_result.append_error(
                    yaml_path="aggregation_component",
                    message="aggregation_component is missing 'outputs' attribute;"
                    + " it does not appear to be a valid component that can be used in a scatter-gather loop.",
                )
            else:
                agg_outputs = aggregation_component.outputs

        # validate silos configs
        if silo_configs is None:
            validation_result.append_error(
                yaml_path="silo_configs",
                message="silo_configs is a required argument for the scatter gather node.",
            )
        elif len(silo_configs) == 0:
            validation_result.append_error(
                yaml_path="silo_configs",
                message="silo_configs cannot be an empty list.",
            )
        else:
            first_silo = silo_configs[0]
            expected_inputs = []
            if hasattr(first_silo, "inputs"):
                expected_inputs = first_silo.inputs.keys()
            num_expected_inputs = len(expected_inputs)
            # pylint: disable=consider-using-enumerate
            for i in range(len(silo_configs)):
                silo = silo_configs[i]
                if not hasattr(silo, "compute"):
                    validation_result.append_error(
                        yaml_path="silo_configs",
                        message=f"Silo at index {i} in silo_configs is missing its compute value.",
                    )
                if not hasattr(silo, "datastore"):
                    validation_result.append_error(
                        yaml_path="silo_configs",
                        message=f"Silo at index {i} in silo_configs is missing its datastore value.",
                    )
                silo_input_len = 0
                if hasattr(silo, "inputs"):
                    silo_input_len = len(silo.inputs)
                    # if inputs exist, make sure the inputs names are consistent across silo configs
                    for expected_input_name in expected_inputs:
                        if expected_input_name not in silo.inputs:
                            validation_result.append_error(
                                yaml_path="silo_configs",
                                message=f"Silo at index {i} has is missing inputs named '{expected_input_name}',"
                                + "which was listed in the first silo config. "
                                + "Silos must have consistent inputs names.",
                            )
                if silo_input_len != num_expected_inputs:
                    validation_result.append_error(
                        yaml_path="silo_configs",
                        message=f"Silo at index {i} has {silo_input_len} inputs, but the first silo established that"
                        + f"each silo would have {num_expected_inputs} silo-specific inputs.",
                    )

        # Make sure both aggregation overrides are set, or not
        if aggregation_datastore is None and aggregation_compute is not None:
            validation_result.append_error(
                yaml_path="aggregation_datastore",
                message="aggregation_datastore cannot be unset if aggregation_compute is set.",
            )
        elif aggregation_datastore is not None and aggregation_compute is None:
            validation_result.append_error(
                yaml_path="aggregation_compute",
                message="aggregation_compute cannot be unset if aggregation_datastore is set.",
            )

        # validate component kwargs, ensuring that the relevant components contain the specified inputs
        if shared_silo_kwargs is None:
            validation_result.append_error(
                yaml_path="shared_silo_kwargs",
                message="shared_silo_kwargs should never be None. Input an empty dictionary instead.",
            )
        elif silo_inputs is not None:
            for k in shared_silo_kwargs.keys():
                if k not in silo_inputs:
                    validation_result.append_error(
                        yaml_path="shared_silo_kwargs",
                        message=f"shared_silo_kwargs keyword {k} not listed in silo_component's inputs",
                    )
        if aggregation_kwargs is None:
            validation_result.append_error(
                yaml_path="aggregation_kwargs",
                message="aggregation_kwargs should never be None. Input an empty dictionary instead.",
            )
        elif silo_inputs is not None:
            for k in aggregation_kwargs.keys():
                if k not in agg_inputs:
                    validation_result.append_error(
                        yaml_path="aggregation_kwargs",
                        message=f"aggregation_kwargs keyword {k} not listed in aggregation_component's inputs",
                    )

        # validate that argument mappings leverage inputs and outputs that actually exist
        if aggregation_to_silo_argument_map is None:
            validation_result.append_error(
                yaml_path="aggregation_to_silo_argument_map",
                message="aggregation_to_silo_argument_map should never be None. Input an empty dictionary instead.",
            )
        elif silo_inputs is not None and agg_outputs is not None:
            for k, v in aggregation_to_silo_argument_map.items():
                if k not in agg_outputs:
                    validation_result.append_error(
                        yaml_path="aggregation_to_silo_argument_map",
                        message=f"aggregation_to_silo_argument_map key {k} "
                        + "is not a known output of the aggregation component.",
                    )
                if v not in silo_inputs:
                    validation_result.append_error(
                        yaml_path="aggregation_to_silo_argument_map",
                        message=f"aggregation_to_silo_argument_map value {v} "
                        + "is not a known input of the silo component.",
                    )
        # and check the other mapping
        if silo_to_aggregation_argument_map is None:
            validation_result.append_error(
                yaml_path="silo_to_aggregation_argument_map",
                message="silo_to_aggregation_argument_map should never be None. "
                + "Input an empty dictionary instead.",
            )
        elif agg_inputs is not None and silo_outputs is not None:
            for k, v in silo_to_aggregation_argument_map.items():
                if k not in silo_outputs:
                    validation_result.append_error(
                        yaml_path="silo_to_aggregation_argument_map",
                        message=f"silo_to_aggregation_argument_map key {k }"
                        + " is not a known output of the silo component.",
                    )
                if v not in agg_inputs:
                    validation_result.append_error(
                        yaml_path="silo_to_aggregation_argument_map",
                        message=f"silo_to_aggregation_argument_map value {v}"
                        + " is not a known input of the aggregation component.",
                    )

        if max_iterations < 1:
            validation_result.append_error(
                yaml_path="max_iterations",
                message=f"max_iterations must be a positive value, not '{max_iterations}'.",
            )

        return validation_result.try_raise(
            cls._get_validation_error_target(),
            raise_error=raise_error,
        )

    @classmethod
    def _custom_fl_data_path(
        cls,
        datastore_name,
        output_name,
        unique_id="${{name}}",
        iteration_num="${{iteration_num}}",
    ):
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

    def _get_aggregator_input_name(self, silo_output_name):
        """
        Returns aggregator input name that maps to silo_output.
        Returns None if silo_output_name not in silo_to_aggregation_argument_map
        """
        return self.silo_to_aggregation_argument_map.get(silo_output_name)

    @classmethod
    def _try_create_default_mappings(
        cls,
        silo_comp: Component,
        agg_comp: Component,
        silo_agg_map: Dict,
        agg_silo_map: Dict,
    ):
        """
        This function tries to produce dictionaries that link the silo and aggregation
        components' outputs to the other's inputs.
        The mapping only occurs for inputted mappings that are None, otherwise
        the inputted mapping is returned unchanged.
        These auto-generated mappings are naive, and simply maps all outputs of a component that have a
        identically-named input in the other component.

            This function does nothing if either inputted component is None. This function will also do nothing
        for a given mapping if either of the relevant inputs or outputs are None (but not empty).

        Returns a tuple of the potentially modified silo to aggregation mapping,
        followed by the aggregation to silo mapping.

        Example inputs:
            silo_comp.inputs = {"silo_input" : value }
            silo_comp.outputs =  {"c" : ..., "silo_output2" : ... }
            agg_comp.inputs = {"silo_output1" : ... }
            agg_comp.outputs = {"agg_output" : ... }
            silo_agg_map = None
            agg_silo_map = {}

        Example returns:
            {"silo_output1" : "silo_output1"}, {}

        """
        if silo_comp is None or agg_comp is None:
            return silo_agg_map, agg_silo_map
        if silo_agg_map is None and silo_comp.outputs is not None and agg_comp.inputs is not None:
            silo_agg_map = {output: output for output in silo_comp.outputs.keys() if output in agg_comp.inputs}
        if agg_silo_map is None:
            agg_silo_map = {output: output for output in agg_comp.outputs.keys() if output in silo_comp.inputs}
        return silo_agg_map, agg_silo_map

    @staticmethod
    def _get_merge_component(output_type):
        """
        Gets the merge component to be used based on type of output
        """
        return MERGE_COMPONENT_MAPPING[output_type]

    def _inject_merge_components(self, executed_silo_components):
        """Add a merge component for each silo output in the silo_to_aggregation_argument_map.
            These merge components act as a mediator between the user silo and aggregation steps, reducing
            the variable number of silo outputs into a single input for the aggergation step.

        Args:
            executed_silo_components: A list of executed silo steps to extract outputs from.
        Returns:
            merge_comp_mapping (dict): A mapping from silo output names to the corresponding newly
                created and executed merge component
        """
        executed_component = executed_silo_components[0]

        merge_comp_mapping = {}
        for (
            silo_output_argument_name,
            _,
        ) in self.silo_to_aggregation_argument_map.items():
            merge_comp = self._get_merge_component(executed_component.outputs[silo_output_argument_name].type)
            merge_component_inputs = {
                silo_output_argument_name
                + "_silo_"
                + str(i): executed_silo_components[i].outputs[silo_output_argument_name]
                for i in range(0, len(executed_silo_components))
            }
            executed_merge_component = merge_comp(**merge_component_inputs)
            for input_obj in executed_merge_component.inputs.values():
                input_obj.mode = "direct"
            for output_obj in executed_merge_component.outputs.values():
                output_obj.type = "mltable"
            merge_comp_mapping.update({silo_output_argument_name: executed_merge_component})

        return merge_comp_mapping

    # boilerplate functions - largely copied from other node builders

    @property
    def outputs(self) -> Dict[str, Union[str, Output]]:
        return self._outputs

    @classmethod
    def _create_schema_for_validation(cls, context) -> PathAwareSchema:
        return FLScatterGatherSchema(context=context)

    def _to_rest_object(self, **kwargs) -> dict:  # pylint: disable=unused-argument
        """Convert self to a rest object for remote call."""
        rest_node = super(FLScatterGather, self)._to_rest_object(**kwargs)
        rest_node.update(dict(outputs=self._to_rest_outputs()))
        return convert_ordered_dict_to_dict(rest_node)
