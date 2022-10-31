# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file stores functions and objects that will be used in mldesigner package.
DO NOT change the module names in "all" list. If the interface has changed in source code, wrap it here and keep
original function/module names the same as before, otherwise mldesigner will be broken by this change.
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from azure.ai.ml import(
    Input,
    Output,
    MLClient,
    load_component,
    MpiDistribution,
    PyTorchDistribution,
    TensorFlowDistribution,
)
from azure.ai.ml.entities import(
    Component,
    CommandComponent,
    PipelineComponent,
    Environment,
    ResourceConfiguration,
    ValidationResult,
    Command,
    Pipeline,
    Parallel,
)
from azure.identity import AzureCliCredential
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

assert hasattr(Component, "_customized_validate")
assert hasattr(Component, "_source_path")
assert hasattr(CommandComponent, "_to_dict")
assert hasattr(CommandComponent, "_source_path")
assert hasattr(PipelineComponent, "_to_dict")
assert hasattr(PipelineComponent, "_source_path")
assert hasattr(PipelineComponent, "jobs")
assert hasattr(InternalComponent, "_to_dict")
assert hasattr(InternalComponent, "_source_path")
assert hasattr(InternalComponent, "_additional_includes")
assert hasattr(_AdditionalIncludes, "with_includes")
assert hasattr(_AdditionalIncludes, "_code_path")
assert hasattr(_AdditionalIncludes, "_includes")
assert hasattr(ValidationResult, "passed")
assert hasattr(ValidationResult, "error_messages")
assert hasattr(ErrorTarget, "PIPELINE")

input_obj = Input()
assert hasattr(input_obj, "type")
assert hasattr(input_obj, "_is_enum")
assert hasattr(input_obj, "default")
assert hasattr(input_obj, "min")
assert hasattr(input_obj, "max")
assert hasattr(input_obj, "optional")
assert hasattr(input_obj, "_is_literal")
assert hasattr(input_obj, "max")
assert hasattr(input_obj, "_get_python_builtin_type_str")
assert hasattr(input_obj, "_get_param_with_standard_annotation")


__all__ = [
    "Input",
    "Output",
    "MLClient",
    "load_component",
    "MpiDistribution",
    "PyTorchDistribution",
    "TensorFlowDistribution",
    "Component",
    "CommandComponent",
    "PipelineComponent",
    "Environment",
    "ResourceConfiguration",
    "ValidationResult",
    "component_factory_load_from_dict",
    "Command",
    "Parallel",
    "Pipeline",
    "load_yaml",
    "SchemaValidatableMixin",
    "PathAwareSchema",
    "AzureCliCredential",
    "UserErrorException",
    "_sanitize_python_variable_name",
    "_generate_component_function",
    "Ae365exepool",
    "InternalCommand",
    "InternalParallel",
    "DataTransfer",
    "Distributed",
    "HDInsight",
    "Hemera",
    "Scope",
    "Starlite",
]