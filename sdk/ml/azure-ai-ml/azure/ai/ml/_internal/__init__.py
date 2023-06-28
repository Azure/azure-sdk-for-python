# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._setup import enable_internal_components_in_pipeline
from .entities import (
    Ae365exepool,
    AISuperComputerConfiguration,
    AISuperComputerScalePolicy,
    AISuperComputerStorageReferenceConfiguration,
    Command,
    DataTransfer,
    Distributed,
    HDInsight,
    Hemera,
    InternalInput,
    ITPConfiguration,
    ITPInteractiveConfiguration,
    ITPPriorityConfiguration,
    ITPResourceConfiguration,
    ITPRetrySettings,
    Parallel,
    Pipeline,
    Scope,
    Starlite,
    TargetSelector,
)

# enable internal components if users has imported this module directly
enable_internal_components_in_pipeline()

__all__ = [
    "TargetSelector",
    "ITPInteractiveConfiguration",
    "ITPPriorityConfiguration",
    "ITPResourceConfiguration",
    "ITPRetrySettings",
    "ITPConfiguration",
    "AISuperComputerConfiguration",
    "AISuperComputerScalePolicy",
    "AISuperComputerStorageReferenceConfiguration",
    "Command",
    "Distributed",
    "Parallel",
    "Scope",
    "DataTransfer",
    "Ae365exepool",
    "HDInsight",
    "Starlite",
    "Pipeline",
    "Hemera",
    "InternalInput",
]
