# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from marshmallow import INCLUDE

from azure.ai.ml._internal._schema.command import CommandSchema, DistributedSchema, ParallelSchema
from azure.ai.ml._internal._schema.component import NodeType
from azure.ai.ml._internal._schema.node import HDInsightSchema, InternalBaseNodeSchema, ScopeSchema
from azure.ai.ml._internal.entities import (
    Command,
    Distributed,
    HDInsight,
    InternalBaseNode,
    InternalComponent,
    Parallel,
    Scope,
    DataTransfer,
    Hemera,
    Starlite,
)
from azure.ai.ml._schema import NestedField
from azure.ai.ml.entities._component.component_factory import component_factory
from azure.ai.ml.entities._job.pipeline._load_component import pipeline_node_factory


def _enable_internal_components():
    create_schema_func = InternalComponent._create_schema_for_validation
    for _type in NodeType.all_values():
        component_factory.register_type(
            _type=_type,
            create_instance_func=lambda: InternalComponent.__new__(InternalComponent),
            create_schema_func=create_schema_func,
        )


_registered = False


def _register_node(_type, node_cls, schema_cls):
    pipeline_node_factory.register_type(
        _type=_type,
        create_instance_func=lambda: node_cls.__new__(node_cls),
        load_from_rest_object_func=node_cls._from_rest_object,
        nested_schema=NestedField(schema_cls, unknown=INCLUDE),
    )


def enable_internal_components_in_pipeline():
    global _registered  # pylint: disable=global-statement
    if _registered:
        return  # already registered

    _enable_internal_components()
    for _type in NodeType.all_values():
        # if we do not register node class for all node types, the only difference will be the type of created node
        # instance (Ae365exepool => InternalBaseNode). Not sure if this is acceptable.
        _register_node(_type, InternalBaseNode, InternalBaseNodeSchema)

    # redo the registration for those with specific runsettings
    _register_node(NodeType.DATA_TRANSFER, DataTransfer, InternalBaseNodeSchema)
    _register_node(NodeType.HEMERA, Hemera, InternalBaseNodeSchema)
    _register_node(NodeType.STARLITE, Starlite, InternalBaseNodeSchema)
    _register_node(NodeType.COMMAND, Command, CommandSchema)
    _register_node(NodeType.DISTRIBUTED, Distributed, DistributedSchema)
    _register_node(NodeType.SCOPE, Scope, ScopeSchema)
    _register_node(NodeType.PARALLEL, Parallel, ParallelSchema)
    _register_node(NodeType.HDI, HDInsight, HDInsightSchema)
    _registered = True
