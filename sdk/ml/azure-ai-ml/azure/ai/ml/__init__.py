# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from .entities._job.distribution import MpiDistribution, PyTorchDistribution, TensorFlowDistribution

from ._ml_client import MLClient
import logging
from ._utils.utils import initialize_logger_info
from azure.ai.ml.entities._inputs_outputs import Input, Output
from .entities._builders.command_func import command

# from .entities._builders.parallel_func import parallel
from azure.ai.ml._restclient.v2022_02_01_preview.models import ManagedIdentity, AmlToken, UserIdentity

from .entities._load_functions import (
    load_batch_deployment,
    load_batch_endpoint,
    load_component,
    load_compute,
    load_data,
    load_datastore,
    load_model,
    load_environment,
    load_job,
    load_online_deployment,
    load_online_endpoint,
    load_workspace,
    load_workspace_connection,
)

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="\n")

__all__ = [
    "MLClient",
    "command",
    #    "parallel",
    "Input",
    "Output",
    "MpiDistribution",
    "PyTorchDistribution",
    "TensorFlowDistribution",
    "ManagedIdentity",
    "AmlToken",
    "UserIdentity",
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
    "load_workspace_connection",
]
