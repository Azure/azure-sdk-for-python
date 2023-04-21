# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

import logging

# from .entities._builders.parallel_func import parallel
from azure.ai.ml.entities._inputs_outputs import Input, Output

from ._ml_client import MLClient
from ._utils._logger_utils import initialize_logger_info
from ._version import VERSION
from .entities._builders.command_func import command
from .entities._builders.spark_func import spark
from .entities._credentials import AmlTokenConfiguration, ManagedIdentityConfiguration, UserIdentityConfiguration
from .entities._job.distribution import MpiDistribution, PyTorchDistribution, TensorFlowDistribution, RayDistribution
from .entities._load_functions import (
    load_batch_deployment,
    load_batch_endpoint,
    load_component,
    load_compute,
    load_data,
    load_datastore,
    load_environment,
    load_job,
    load_model,
    load_online_deployment,
    load_online_endpoint,
    load_registry,
    load_workspace,
    load_workspace_connection,
    load_model_package,
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
    "ManagedIdentityConfiguration",
    "AmlTokenConfiguration",
    "UserIdentityConfiguration",
    "load_batch_deployment",
    "load_batch_endpoint",
    "load_component",
    "load_compute",
    "load_data",
    "load_datastore",
    "load_model",
    "load_environment",
    "load_job",
    "load_online_deployment",
    "load_online_endpoint",
    "load_workspace",
    "load_registry",
    "load_workspace_connection",
    "load_model_package",
]

__version__ = VERSION
