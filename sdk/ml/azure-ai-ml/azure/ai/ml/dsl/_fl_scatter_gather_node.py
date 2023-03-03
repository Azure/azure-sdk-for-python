# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import List, Dict, Optional

from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml._utils._experimental import experimental

@experimental
def fl_scatter_gather(
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
    _pass_iteration_to_components: bool = False,
    _pass_index_to_silo_components: bool = False,
    _create_default_mappings_if_needed: bool = False,
    **kwargs,
):
    """
    param silo_component: A component which contains the steps that will be run multiple
        times across different silos, as specified by the silo_configs input. In a typical
        horizontal federated learning context, this component is what will perform actual model
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
