# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import List, Dict


from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml._utils._experimental import experimental

# This should be the implementation of what's used in the spec here:
# https://github.com/Azure/azureml_run_specification/blob/aims/flspec/specs/federated-learning/examples/sdk/1_preprocessing.py#L189
# General idea, this node will be used to warp code snippets into in a scatter gather loop
# for FL learning.
#
# Here's some example pseudocode usage. The output of FLScatterGather(inputs) is a node which,
# when included in the definition of a @pipeline function, will produce a subgraph that performs
# a scatter-gather loop in AML:
#
# @pipeline(name = "example_fl_pipeline")
# pipeline_func():
#   fl_node = FLScatterGather(
#     model=get_initial_model(),
#     silo_configs=silo_config_list,
#     learning_func=train_model_func,
#     aggregation_func=gather_models_func,
#     max_iterations=100)
#   return {pipeline_output : fl_node.output}
# ...
# fl_pipeline = pipeline_func()
# ml_client.jobs.create_or_update(fl_pipeline, experiment_name="fl_pipeline")
#
#
#
# We can hopefully leverage a lot of code from the example project to achieve this:
# https://github.com/Azure/DesignerPrivatePreviewFeatures/tree/d8732de8f3f201aebeac2f079f8f89e3592be2ba/azure-ai-ml/samples/control-flow/federated-learning/native
# At a high level, I believe we just want to turn the following code into it's own decorator, with a few changes:
# https://github.com/Azure/DesignerPrivatePreviewFeatures/blob/d8732de8f3f201aebeac2f079f8f89e3592be2ba/azure-ai-ml/samples/control-flow/federated-learning/native/main.py#L87
#  Changes include:
#  - Expand inputs to match spec
#  - Possibly encapsulate entire scatter/gather loop with a do-while loop (individual scatters will be managed by a parallel-for loop).
#     - See https://github.com/Azure/DesignerPrivatePreviewFeatures/blob/d8732de8f3f201aebeac2f079f8f89e3592be2ba/azure-ai-ml/samples/control-flow/federated-learning/native/main.py#L151
#     - And for p-for: https://azureml-pipelines-doc-1p.azurewebsites.net/features/control_flow/parallel_for.html
#  - change output to be... whatever the standard output of a model training step is.
#
# TODO decide on default values for this, and remove defaults from either here or builder.
@experimental
def fl_scatter_gather(
    *,
    silo_configs: List[FederatedLearningSilo],
    silo_component: Component,
    aggregation_component: Component,
    aggregation_compute: str = None,
    aggregation_datastore: str = None,
    shared_silo_kwargs: Dict = None,
    aggregation_kwargs: Dict = None,
    silo_to_aggregation_argument_map: Dict = None,
    aggregation_to_silo_argument_map: Dict = None,
    max_iterations: int = 1,
    _pass_iteration_to_components: bool = False,
    _pass_index_to_silo_components: bool = False,
    _create_default_mappings_if_needed: bool = False,
    **kwargs,
):
    """
    param silo_component: A component which contains the steps that will be run multiple
        times across different silos, as specified by the silo_configs input. In a typical
        horizonal federated learning context, this component is what will perform actual model
        training.
    type silo_component: Component
    param aggregation_component: A component which receives inputs from the myriad executed silo components,
        and does something with them. In a typical horizontal federated learning context, this component
        will merge the models that were independently trained on each silo's data in a single model.
    type aggregation_component: Component
        param silo_configs: A list of FederatedLearningSilo objects, which contain the necessary data
        to reconfigure components to run on specific computes and datastores, while also targeting
        specific inputs located on the aforementioned datastores.
    type silo_configs: List[FederatedLearningSilo]
    param aggregation_compute: The name of the compute that the aggregation component will use.
    type aggregation_compute: string
    param aggregation_datastore: The name of the datastore that the aggregation component will use.
    type aggregation_datastore: string
    param shared_silo_kwargs: A dictionary of string keywords to component inputs. This dictionary is treated
        like kwargs, and is injected into ALL executed silo components.
    type shared_silo_kwargs: Dict
    param aggregation_kwargs: A dictionary of string keywords to component inputs. This dictionary is treated
        like kwargs, and is injected into ALL executed aggregation components.
    type aggregation_kwargs: Dict
    param max_iterations: The maximum number of scatter gather iterations that should be performed.
    type max_iterations: int
    """
    # Private kwargs:
    # _pass_iteration_to_components: to be changed
    # _pass_index_to_silo_components: to be changed
    # _create_default_mappings_if_needed: if true, then try to automatically create i/o mappings if they're unset.

    # Like most nodes, this is just a wrapper around a node builder entity initializer.
    return FLScatterGather(
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
        pass_iteration_to_components=_pass_iteration_to_components,
        pass_index_to_silo_components=_pass_index_to_silo_components,
        create_default_mappings_if_needed=_create_default_mappings_if_needed,
        **kwargs,
    )
