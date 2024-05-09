# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging
from typing import Any, Optional

# from .entities._builders.parallel_func import parallel
from azure.ai.ml.entities._inputs_outputs import Input, Output

from ._ml_client import MLClient
from ._utils._logger_utils import initialize_logger_info
from ._version import VERSION
from .entities._builders.command_func import command
from .entities._builders.spark_func import spark
from .entities._job.distribution import MpiDistribution, PyTorchDistribution, RayDistribution, TensorFlowDistribution
from .entities._load_functions import (
    load_batch_deployment,
    load_batch_endpoint,
    load_component,
    load_compute,
    load_connection,
    load_data,
    load_datastore,
    load_environment,
    load_feature_set,
    load_feature_store,
    load_feature_store_entity,
    load_index,
    load_job,
    load_marketplace_subscription,
    load_model,
    load_model_package,
    load_online_deployment,
    load_online_endpoint,
    load_registry,
    load_serverless_endpoint,
    load_workspace,
    load_workspace_connection,
)

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="\n")

__all__ = [
    "MLClient",
    "command",
    "spark",
    # "parallel",
    "Input",
    "Output",
    "MpiDistribution",
    "PyTorchDistribution",
    "TensorFlowDistribution",
    "RayDistribution",
    "load_batch_deployment",
    "load_batch_endpoint",
    "load_component",
    "load_compute",
    "load_data",
    "load_datastore",
    "load_feature_set",
    "load_feature_store",
    "load_feature_store_entity",
    "load_index",
    "load_model",
    "load_environment",
    "load_job",
    "load_online_deployment",
    "load_online_endpoint",
    "load_workspace",
    "load_registry",
    "load_connection",
    "load_workspace_connection",
    "load_model_package",
    "load_marketplace_subscription",
    "load_serverless_endpoint",
]

__version__ = VERSION


# Allow importing these types for backwards compatibility


def __getattr__(name: str):
    requested: Optional[Any] = None

    if name == "AmlTokenConfiguration":
        from .entities._credentials import AmlTokenConfiguration

        requested = AmlTokenConfiguration
    if name == "ManagedIdentityConfiguration":
        from .entities._credentials import ManagedIdentityConfiguration

        requested = ManagedIdentityConfiguration
    if name == "UserIdentityConfiguration":
        from .entities._credentials import UserIdentityConfiguration

        requested = UserIdentityConfiguration

    if requested:
        if not getattr(__getattr__, "warning_issued", False):
            logging.warning(
                " %s will be removed from the azure.ai.ml namespace in a future release."
                " Please use the azure.ai.ml.entities namespace instead.",
                name,
            )
            __getattr__.warning_issued = True  # type: ignore[attr-defined]
        return requested

    raise AttributeError(f"module 'azure.ai.ml' has no attribute {name}")
