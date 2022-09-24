# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

DO_WHILE_MAX_ITERATION = 1000


class ComponentJobConstants(object):
    INPUT_PATTERN = r"^\$\{\{parent\.(inputs|jobs)\.(.*?)\}\}$"
    OUTPUT_PATTERN = r"^\$\{\{parent\.outputs\.(.*?)\}\}$"
    LEGACY_INPUT_PATTERN = r"^\$\{\{(inputs|jobs)\.(.*?)\}\}$"
    LEGACY_OUTPUT_PATTERN = r"^\$\{\{outputs\.(.*?)\}\}$"
    INPUT_DESTINATION_FORMAT = "jobs.{}.inputs.{}"
    OUTPUT_DESTINATION_FORMAT = "jobs.{}.outputs.{}"


class NodeType(object):
    COMMAND = "command"
    SWEEP = "sweep"
    PARALLEL = "parallel"
    AUTOML = "automl"
    PIPELINE = "pipeline"
    IMPORT = "import"
    SPARK = "spark"
    # Note: container is not a real component type,
    # only used to mark component from container data.
    _CONTAINER = "_container"


class ControlFlowType(object):
    DO_WHILE = "do_while"
    IF_ELSE = "if_else"


class ComponentSource:
    """Indicate where the component is constructed."""

    BUILDER = "BUILDER"
    DSL = "DSL"
    CLASS = "CLASS"
    REMOTE_WORKSPACE_JOB = "REMOTE.WORKSPACE.JOB"
    REMOTE_WORKSPACE_COMPONENT = "REMOTE.WORKSPACE.COMPONENT"
    REMOTE_REGISTRY = "REMOTE.REGISTRY"
    YAML_JOB = "YAML.JOB"
    YAML_COMPONENT = "YAML.COMPONENT"


class ParallelTaskType:
    RUN_FUNCTION = "run_function"
    FUNCTION = "function"
    MODEL = "model"


class ComponentParameterTypes:
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    STRING = "string"


class IOConstants:
    PRIMITIVE_STR_2_TYPE = {
        ComponentParameterTypes.INTEGER: int,
        ComponentParameterTypes.STRING: str,
        ComponentParameterTypes.NUMBER: float,
        ComponentParameterTypes.BOOLEAN: bool,
    }
    PRIMITIVE_TYPE_2_STR = {
        int: ComponentParameterTypes.INTEGER,
        str: ComponentParameterTypes.STRING,
        float: ComponentParameterTypes.NUMBER,
        bool: ComponentParameterTypes.BOOLEAN,
    }
    TYPE_MAPPING_YAML_2_REST = {
        ComponentParameterTypes.STRING: "String",
        ComponentParameterTypes.INTEGER: "Integer",
        ComponentParameterTypes.NUMBER: "Number",
        ComponentParameterTypes.BOOLEAN: "Boolean",
    }
    PARAM_PARSERS = {
        ComponentParameterTypes.INTEGER: lambda v: int(float(v)),  # parse case like 10.0 -> 10
        ComponentParameterTypes.BOOLEAN: lambda v: str(v).lower() == "true",
        ComponentParameterTypes.NUMBER: float,
    }
    # For validation, indicates specific parameters combination for each type
    INPUT_TYPE_COMBINATION = {
        "uri_folder": ["path", "mode"],
        "uri_file": ["path", "mode"],
        "mltable": ["path", "mode"],
        "mlflow_model": ["path", "mode"],
        "custom_model": ["path", "mode"],
        "integer": ["default", "min", "max"],
        "number": ["default", "min", "max"],
        "string": ["default"],
        "boolean": ["default"],
    }
    GROUP_ATTR_NAME = "__parameter_group__"
    GROUP_TYPE_NAME = "group"
