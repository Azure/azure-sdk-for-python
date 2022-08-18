# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from marshmallow import INCLUDE

from azure.ai.ml._internal._schema.command import CommandSchema, DistributedSchema
from azure.ai.ml._internal._schema.component import NodeType
from azure.ai.ml._internal._schema.node import InternalBaseNodeSchema
from azure.ai.ml._internal._schema.scope import ScopeSchema
from azure.ai.ml._internal.entities import Command, Distributed, Scope, InternalComponent, InternalBaseNode
from azure.ai.ml._schema import NestedField
from azure.ai.ml.constants import IOConstants
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

    # hack - internal primitive type
    float_primitive_type = "float"
    IOConstants.PRIMITIVE_STR_2_TYPE[float_primitive_type] = float
    IOConstants.PARAM_PARSERS[float_primitive_type] = float
    IOConstants.TYPE_MAPPING_YAML_2_REST[float_primitive_type] = "Float"

    # TODO: do we support both Enum & enum?
    enum_primitive_type = "Enum"
    IOConstants.PRIMITIVE_STR_2_TYPE[enum_primitive_type] = str
    IOConstants.TYPE_MAPPING_YAML_2_REST[enum_primitive_type] = "Enum"

    enum_primitive_type = "enum"
    IOConstants.PRIMITIVE_STR_2_TYPE[enum_primitive_type] = str
    IOConstants.TYPE_MAPPING_YAML_2_REST[enum_primitive_type] = "enum"


def _enable_internal_components_in_pipeline():
    _enable_internal_components()
    for _type in NodeType.all_values():
        # if we do not register node class for all node types, the only difference will be the type of created node
        # instance (Ae365exepool => InternalBaseNode). Not sure if this is acceptable.
        pipeline_node_factory.register_type(
            _type=_type,
            create_instance_func=lambda: InternalBaseNode.__new__(InternalBaseNode),
            load_from_rest_object_func=InternalBaseNode._from_rest_object,
            nested_schema=NestedField(InternalBaseNodeSchema, unknown=INCLUDE),
        )

    # redo the registration for those with specific runsettings
    pipeline_node_factory.register_type(
        _type=NodeType.COMMAND,
        create_instance_func=lambda: Command.__new__(Command),
        load_from_rest_object_func=Command._from_rest_object,
        nested_schema=NestedField(CommandSchema, unknown=INCLUDE),
    )
    pipeline_node_factory.register_type(
        _type=NodeType.DISTRIBUTED,
        create_instance_func=lambda: Distributed.__new__(Distributed),
        load_from_rest_object_func=Distributed._from_rest_object,
        nested_schema=NestedField(DistributedSchema, unknown=INCLUDE),
    )
    pipeline_node_factory.register_type(
        _type=NodeType.SCOPE,
        create_instance_func=lambda: Scope.__new__(Scope),
        load_from_rest_object_func=Scope._from_rest_object,
        nested_schema=NestedField(ScopeSchema, unknown=INCLUDE),
    )
