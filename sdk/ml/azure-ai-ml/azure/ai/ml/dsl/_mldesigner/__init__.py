# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file stores functions and objects that will be used in mldesigner package.
DO NOT change the module names in "all" list. If the interface has changed in source code, wrap it here and keep
original function/module names the same as before, otherwise mldesigner will be broken by this change.
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from azure.ai.ml.exceptions import ErrorTarget, UserErrorException
from azure.ai.ml.entities._component.component_factory import component_factory
from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function
from azure.ai.ml._internal.entities._additional_includes import _AdditionalIncludes
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities._validation import SchemaValidatableMixin
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.dsl._utils import _sanitize_python_variable_name
from azure.ai.ml._internal.entities import (
    InternalComponent,
    Ae365exepool,
    Command as InternalCommand,
    Parallel as InternalParallel,
    DataTransfer,
    Distributed,
    HDInsight,
    Hemera,
    Scope,
    Starlite,
)

component_factory_load_from_dict = component_factory.load_from_dict


__all__ = [
    "Ae365exepool",
    "AzureCliCredential",
    "DataTransfer",
    "Distributed",
    "HDInsight",
    "Hemera",
    "InternalCommand",
    "InternalParallel",
    "PathAwareSchema",
    "SchemaValidatableMixin",
    "Scope",
    "Starlite",
    "UserErrorException",
    "_generate_component_function",
    "_sanitize_python_variable_name",
    "component_factory_load_from_dict",
    "load_yaml",
]