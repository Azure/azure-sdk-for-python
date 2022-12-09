# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file stores functions and objects that will be used in mldesigner package.
DO NOT change the module names in "all" list. If the interface has changed in source code, wrap it here and keep
original function/module names the same as before, otherwise mldesigner will be broken by this change.
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from ._constants import V1_COMPONENT_TO_NODE
from azure.ai.ml.exceptions import ErrorTarget
from azure.ai.ml.entities._component.component_factory import component_factory
from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.entities._inputs_outputs.utils import _get_annotation_by_value
from azure.ai.ml.entities._validation import SchemaValidatableMixin
from azure.ai.ml.entities._inputs_outputs import EnumInput, GroupInput, _get_param_with_standard_annotation
from azure.ai.ml.entities._builders.base_node import BaseNode
from azure.ai.ml._internal.entities._additional_includes import _AdditionalIncludes
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._asset_utils import get_ignore_file
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._internal.entities import InternalComponent
from azure.ai.ml.dsl._condition import condition
from azure.ai.ml.dsl._do_while import do_while
from azure.ai.ml.dsl._group_decorator import group
from azure.ai.ml.dsl._dynamic import _assert_arg_valid

component_factory_load_from_dict = component_factory.load_from_dict


__all__ = [
    # maybe not needed
    "BaseNode",
    "ErrorTarget",
    "EnumInput",
    "PathAwareSchema",
    "SchemaValidatableMixin",
    "GroupInput",
    "_assert_arg_valid",
    "_get_annotation_by_value",
    "PipelineInput",

    # to be put in main package
    "condition",
    "do_while",
    "group",

    # must keep
    "experimental",
    "get_ignore_file",
    "_get_param_with_standard_annotation",
    "_generate_component_function",
    "component_factory_load_from_dict",
    "load_yaml",
    "V1_COMPONENT_TO_NODE",

]