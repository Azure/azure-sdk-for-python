# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import importlib

# pylint: disable=protected-access
from typing import Any, Dict, List, Optional, Union

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities import CommandComponent, PipelineJob
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather


def _check_for_import(package_name: str) -> None:
    try:
        # pylint: disable=unused-import
        importlib.import_module(package_name)
    except ImportError as e:
        raise ImportError(
            "The DSL FL Node has an additional requirement above the rest of the "
            + "AML SDK repo in that the mldesigner package is required. Please run `pip install mldesigner` "
            + "and try again."
        ) from e


@experimental
def fl_scatter_gather(
    *,
    silo_configs: List[FederatedLearningSilo],
    silo_component: Union[PipelineJob, CommandComponent],
    aggregation_component: Union[PipelineJob, CommandComponent],
    aggregation_compute: Optional[str] = None,
    aggregation_datastore: Optional[str] = None,
    shared_silo_kwargs: Optional[Dict] = None,
    aggregation_kwargs: Optional[Dict] = None,
    silo_to_aggregation_argument_map: Optional[Dict] = None,
    aggregation_to_silo_argument_map: Optional[Dict] = None,
    max_iterations: int = 1,
    _create_default_mappings_if_needed: bool = False,
    **kwargs: Any,
) -> FLScatterGather:
    """A federated learning scatter-gather subgraph node.

    It's assumed that this will be used inside of a `@pipeline`-decorated function in order to create a subgraph which
    will:
        - Execute a specified pipeline step multiple times (the silo step), with each execution using slightly
            different inputs, datastores, and computes based on an inputted config.
        - Merge the outputs of the multiple silo steps into a single input for another step (the aggregation step),
            which will then process the values into a single unified result.
        - With the process above being a 'scatter gather' sequence, iterate and perform the scatter gather
            a number of times according to the max_iterations input, with the output of any given iteration's
            aggregation step being fed back into the silo steps of the subsequent iteration.
        - Return the outputs of the last iteration's aggregation step as the node's final output.

    The process of assigning computes, datastores, and inputs to steps is called 'anchoring'. The following
    details of the anchoring process should be noted:
        - Computes will always be overridden to their respective compute.
        - The paths of 'internal' outputs for silo steps (i.e. a component output that becomes an input for another
            component within the silo step) are anchored to that silo's datastore. All other outputs are anchored
            to the aggregation datastore.
        - Some steps are automatically created by this node to merge inputs from the silo steps to the aggregation
            step. These steps are anchored in the same manner as the aggregation step.
        - Datastore anchoring ONLY occurs if an output's path value is empty. If a path already exists, it will NOT
            try to replace it.

    The process of trimming down inputs from the silo steps to a single input for the aggregate step has some
    caveats:
        - Only silo outputs of type mltable and uri_folder are supported.
        - Both the above output types become an mltable which mounts all the silo step outputs as sub-folders.

    The expected use case of this node is shown in the following code snippet:

    .. code-block:: python

        @experimental
        def fl_pipeline():
            fl_node = fl_scatter_gather(**many_inputs)
            return {"pipeline_output" : fl_node.outputs["aggregated_model"]}

        submitted_pipeline_job = my_client.jobs.create_or_update(fl_pipeline(), experiment_name="example_fl_pipeline")

    :keyword silo_configs: A list of FederatedLearningSilo objects,
        which contain the necessary data to reconfigure components to run on specific computes and datastores,
        while also targeting specific inputs located on the aforementioned datastores.
    :paramtype silo_configs: List[~azure.ai.ml.entities._assets.federated_learning_silo.FederatedLearningSilo]
    :keyword silo_component: A pipeline step that will be run multiple times across different silos, as specified
        by the silo_configs input. In a typical horizontal federated learning context, this step is what will perform
        model training using siloed subsets of data. Can be either a PipelineJob or a CommandComponent.
    :paramtype silo_component: Union[~azure.ai.ml.entities.PipelineJob, ~azure.ai.ml.entities.CommandComponent]
    :keyword aggregation_component: A pipeline step which receives inputs from the myriad executed silo components,
        and does something with them. In a typical horizontal federated learning context, this component will merge
        the models that were independently trained on each silo's data in a single model. Can be either a
        PipelineJob or a CommandComponent.
    :paramtype aggregation_component: Union[
        ~azure.ai.ml.entities.PipelineJob,
        ~azure.ai.ml.entities.CommandComponent]
    :keyword aggregation_compute: The name of the compute that the aggregation component will use.
    :paramtype aggregation_compute: str
    :keyword aggregation_datastore: The name of the datastore that the aggregation component will use.
    :paramtype aggregation_datastore: str
    :keyword shared_silo_kwargs: A dictionary of string keywords to component inputs. This dictionary is treated
        like kwargs and is injected into ALL executed silo components.
    :paramtype shared_silo_kwargs: Dict
    :keyword aggregation_kwargs: A dictionary of string keywords to component inputs. This dictionary is treated
        like kwargs and is injected into ALL executed aggregation components.
    :paramtype aggregation_kwargs: Dict
    :keyword silo_to_aggregation_argument_map: A dictionary specifying the mapping of outputs from the silo step to
        inputs in the aggregation step. The keys should be output names from the silo step, and the values should be
        input names in the aggregation step. This allows for customization of the mapping between the steps.
    :paramtype silo_to_aggregation_argument_map: Dict
    :keyword aggregation_to_silo_argument_map: A dictionary specifying the mapping of outputs from the aggregation step
        to inputs in the silo step. The keys should be output names from the aggregation step, and the values should be
        input names in the silo step. This allows for customization of the mapping between the steps.
    :paramtype aggregation_to_silo_argument_map: Dict
    :keyword max_iterations: The maximum number of scatter gather iterations that should be performed.
    :paramtype max_iterations: int
    :keyword _create_default_mappings_if_needed:
        If True, try to automatically create input/output mappings if they're unset.
    :paramtype _create_default_mappings_if_needed: bool
    :return: The federated learning scatter-gather subgraph node.
    :rtype: ~azure.ai.ml.entities._builders.fl_scatter_gather.FLScatterGather

    .. warning::

        Using this node directly from the SDK repo requires that the user have the 'mldesigner' package installed,
        which is not a standard dependency of this package.
    """
    # Private kwargs:
    # _create_default_mappings_if_needed: if true, then try to automatically create i/o mappings if they're unset.

    # check that mldesigner is available
    _check_for_import("mldesigner")

    # Like other DSL nodes, this is just a wrapper around a node builder entity initializer.
    return FLScatterGather(
        silo_configs=silo_configs,
        silo_component=silo_component,  # type: ignore[arg-type]
        aggregation_component=aggregation_component,  # type: ignore[arg-type]
        shared_silo_kwargs=shared_silo_kwargs,
        aggregation_compute=aggregation_compute,
        aggregation_datastore=aggregation_datastore,
        aggregation_kwargs=aggregation_kwargs,
        silo_to_aggregation_argument_map=silo_to_aggregation_argument_map,
        aggregation_to_silo_argument_map=aggregation_to_silo_argument_map,
        max_iterations=max_iterations,
        create_default_mappings_if_needed=_create_default_mappings_if_needed,
        **kwargs,
    )
