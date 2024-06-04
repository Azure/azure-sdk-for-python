# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import NoReturn

# pylint: disable=protected-access
from marshmallow import INCLUDE

from .._schema import NestedField
from ..entities._builders.control_flow_node import LoopNode
from ..entities._component.component_factory import component_factory
from ..entities._job.pipeline._load_component import pipeline_node_factory
from ._schema.command import CommandSchema, DistributedSchema, ParallelSchema
from ._schema.component import NodeType
from ._schema.node import HDInsightSchema, InternalBaseNodeSchema, ScopeSchema
from .entities import (
    Command,
    DataTransfer,
    Distributed,
    HDInsight,
    Hemera,
    InternalBaseNode,
    InternalComponent,
    Parallel,
    Pipeline,
    Scope,
    Starlite,
)
from .entities.spark import InternalSparkComponent

_registered = False


def _set_registered(value: bool):
    global _registered  # pylint: disable=global-statement
    _registered = value


def _enable_internal_components():
    create_schema_func = InternalComponent._create_schema_for_validation
    for _type in NodeType.all_values():
        component_factory.register_type(
            _type=_type,
            create_instance_func=lambda: InternalComponent.__new__(InternalComponent),
            create_schema_func=create_schema_func,
        )
    component_factory.register_type(
        _type=NodeType.SPARK,
        create_instance_func=lambda: InternalSparkComponent.__new__(InternalSparkComponent),
        create_schema_func=InternalSparkComponent._create_schema_for_validation,
    )


def _register_node(_type, node_cls, schema_cls):
    pipeline_node_factory.register_type(
        _type=_type,
        create_instance_func=lambda: node_cls.__new__(node_cls),
        load_from_rest_object_func=node_cls._from_rest_object,
        nested_schema=NestedField(schema_cls, unknown=INCLUDE),
    )


def enable_internal_components_in_pipeline(*, force=False) -> NoReturn:
    """Enable internal components in pipeline.

    :keyword force: Whether to force re-enable internal components. Defaults to False.
    :type force: bool
    :return: No return value.
    :rtype: None
    """
    if _registered and not force:
        return  # already registered

    _enable_internal_components()
    for _type in NodeType.all_values():
        # if we do not register node class for all node types, the only difference will be the type of created node
        # instance (Ae365exepool => InternalBaseNode). Not sure if this is acceptable.
        _register_node(_type, InternalBaseNode, InternalBaseNodeSchema)

    # redo the registration for those with specific runsettings
    _register_node(NodeType.DATA_TRANSFER, DataTransfer, InternalBaseNodeSchema)
    _register_node(NodeType.COMMAND, Command, CommandSchema)
    _register_node(NodeType.DISTRIBUTED, Distributed, DistributedSchema)
    _register_node(NodeType.PARALLEL, Parallel, ParallelSchema)
    _register_node(NodeType.HEMERA, Hemera, InternalBaseNodeSchema)
    _register_node(NodeType.STARLITE, Starlite, InternalBaseNodeSchema)
    _register_node(NodeType.SCOPE, Scope, ScopeSchema)
    _register_node(NodeType.HDI, HDInsight, HDInsightSchema)

    # register v2 style 1p only components
    _register_node(NodeType.HEMERA_V2, Hemera, InternalBaseNodeSchema)
    _register_node(NodeType.STARLITE_V2, Starlite, InternalBaseNodeSchema)
    _register_node(NodeType.SCOPE_V2, Scope, ScopeSchema)
    _register_node(NodeType.HDI_V2, HDInsight, HDInsightSchema)
    # Ae365exepool and AetherBridge have been registered to InternalBaseNode

    # allow using internal nodes in do-while loop
    LoopNode._extra_body_types = (Command, Pipeline)

    _set_registered(True)
