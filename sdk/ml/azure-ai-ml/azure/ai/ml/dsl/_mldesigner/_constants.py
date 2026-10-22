# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""This file stores constants that will be used in mldesigner package."""
from azure.ai.ml._internal._schema.component import NodeType as V1NodeType
from azure.ai.ml._internal.entities import (
    Ae365exepool,
    AetherBridge,
    Command as InternalCommand,
    Parallel as InternalParallel,
    Pipeline as InternalPipeline,
    DataTransfer,
    Distributed,
    HDInsight,
    Hemera,
    Scope,
    Starlite,
)

V1_COMPONENT_TO_NODE = {
    V1NodeType.SCOPE: Scope,
    V1NodeType.COMMAND: InternalCommand,
    V1NodeType.PARALLEL: InternalParallel,
    V1NodeType.PIPELINE: InternalPipeline,
    V1NodeType.DATA_TRANSFER: DataTransfer,
    V1NodeType.DISTRIBUTED: Distributed,
    V1NodeType.HDI: HDInsight,
    V1NodeType.STARLITE: Starlite,
    V1NodeType.HEMERA: Hemera,
    V1NodeType.AE365EXEPOOL: Ae365exepool,
    V1NodeType.AETHER_BRIDGE: AetherBridge,
}
