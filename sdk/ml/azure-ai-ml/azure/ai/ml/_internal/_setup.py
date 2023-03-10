# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from azure.ai.ml._internal._schema.command import CommandSchema, DistributedSchema, ParallelSchema
from azure.ai.ml._internal._schema.component import NodeType
from azure.ai.ml._internal._schema.node import HDInsightSchema, InternalBaseNodeSchema, ScopeSchema, SparkSchema
from azure.ai.ml._internal.entities import (
    Command,
    DataTransfer,
    Distributed,
    HDInsight,
    Hemera,
    InternalBaseNode,
    InternalComponent,
    Parallel,
    Scope,
    Starlite,
)
from azure.ai.ml._internal.entities.component import InternalSparkComponent
from azure.ai.ml._internal.entities.node import Spark
from azure.ai.ml._schema import NestedField
from azure.ai.ml.entities._component.component_factory import component_factory
from azure.ai.ml.entities._job.pipeline._load_component import pipeline_node_factory
from marshmallow import INCLUDE

_registered = False


def _set_registered(value: bool):
    global _registered  # pylint: disable=global-statement
    _registered = value


def _enable_internal_components():
    create_schema_func = InternalComponent._create_schema_for_validation
    for _type in NodeType.all_values():
        # hack: internal spark is conflict with spark, so we register as INTERNAL_SPARK instead of SPARK
        component_factory.register_type(
            _type=_type,
            create_instance_func=lambda: InternalComponent.__new__(InternalComponent),
            create_schema_func=create_schema_func,
        )
    component_factory.register_type(
        _type=NodeType.INTERNAL_SPARK,
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


def enable_internal_components_in_pipeline(*, force=False):
    global _registered  # pylint: disable=global-statement
    if _registered and not force:
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
    _register_node(NodeType.INTERNAL_SPARK, Spark, SparkSchema)
    _set_registered(True)
