# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""This file stores functions and objects that will be used in mldesigner package.

DO NOT change the module names in "all" list. If the interface has changed in source code, wrap it here and keep
original function/module names the same as before, otherwise mldesigner will be broken by this change.
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from azure.ai.ml.entities._component.component_factory import component_factory
from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function
from azure.ai.ml.entities._inputs_outputs import _get_param_with_standard_annotation
from azure.ai.ml._internal.entities._additional_includes import InternalAdditionalIncludes
from azure.ai.ml._utils._asset_utils import get_ignore_file
from azure.ai.ml._utils.utils import try_enable_internal_components
from azure.ai.ml._internal.entities import InternalComponent
from azure.ai.ml.dsl._condition import condition
from azure.ai.ml.dsl._do_while import do_while
from azure.ai.ml.dsl._parallel_for import parallel_for, ParallelFor
from azure.ai.ml.dsl._group_decorator import group

from ._constants import V1_COMPONENT_TO_NODE

component_factory_load_from_dict = component_factory.load_from_dict


__all__ = [
    # to be put in main package
    "condition",
    "do_while",
    "group",
    "parallel_for",
    "ParallelFor",
    # must keep
    "get_ignore_file",
    "_get_param_with_standard_annotation",
    "_generate_component_function",
    "component_factory_load_from_dict",
    "V1_COMPONENT_TO_NODE",
    "try_enable_internal_components",
    "InternalAdditionalIncludes",
    "InternalComponent",
]
