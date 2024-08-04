# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=line-too-long

from typing import Dict

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
    DATA_TRANSFER = "data_transfer"
    FLOW_PARALLEL = "promptflow_parallel"
    # Note: container is not a real component type,
    # only used to mark component from container data.
    _CONTAINER = "_container"


class ControlFlowType(object):
    DO_WHILE = "do_while"
    IF_ELSE = "if_else"
    PARALLEL_FOR = "parallel_for"


CONTROL_FLOW_TYPES = [getattr(ControlFlowType, k) for k in dir(ControlFlowType) if k.isupper()]


class DataTransferTaskType(object):
    COPY_DATA = "copy_data"
    IMPORT_DATA = "import_data"
    EXPORT_DATA = "export_data"


class DataCopyMode(object):
    MERGE_WITH_OVERWRITE = "merge_with_overwrite"
    FAIL_IF_CONFLICT = "fail_if_conflict"


class ExternalDataType(object):
    FILE_SYSTEM = "file_system"
    DATABASE = "database"


class DataTransferBuiltinComponentUri(object):
    IMPORT_DATABASE = "azureml://registries/azureml/components/import_data_database/versions/0.0.1"
    IMPORT_FILE_SYSTEM = "azureml://registries/azureml/components/import_data_file_system/versions/0.0.1"
    EXPORT_DATABASE = "azureml://registries/azureml/components/export_data_database/versions/0.0.1"


class LLMRAGComponentUri:
    LLM_RAG_CRACK_AND_CHUNK = "azureml://registries/azureml/components/llm_rag_crack_and_chunk/labels/default"
    LLM_RAG_GENERATE_EMBEDDINGS = "azureml://registries/azureml/components/llm_rag_generate_embeddings/labels/default"
    LLM_RAG_CRACK_AND_CHUNK_AND_EMBED = (
        "azureml://registries/azureml/components/llm_rag_crack_and_chunk_and_embed/labels/default"
    )
    LLM_RAG_UPDATE_ACS_INDEX = "azureml://registries/azureml/components/llm_rag_update_acs_index/labels/default"
    LLM_RAG_UPDATE_PINECONE_INDEX = (
        "azureml://registries/azureml/components/llm_rag_update_pinecone_index/labels/default"
    )
    LLM_RAG_CREATE_FAISS_INDEX = "azureml://registries/azureml/components/llm_rag_create_faiss_index/labels/default"
    LLM_RAG_REGISTER_MLINDEX_ASSET = (
        "azureml://registries/azureml/components/llm_rag_register_mlindex_asset/labels/default"
    )
    LLM_RAG_VALIDATE_DEPLOYMENTS = "azureml://registries/azureml/components/llm_rag_validate_deployments/labels/default"
    LLM_RAG_CREATE_PROMPTFLOW = "azureml://registries/azureml/components/llm_rag_create_promptflow/labels/default"


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
    BUILTIN = "BUILTIN"


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
    PARAM_PARSERS: Dict = {
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
    GROUP_ATTR_NAME = "__dsl_group__"
    GROUP_TYPE_NAME = "group"
    # Note: ([a-zA-Z_]+[a-zA-Z0-9_]*) is a valid single key,
    # so a valid pipeline key is: ^{single_key}([.]{single_key})*$
    VALID_KEY_PATTERN = r"^([a-zA-Z_]+[a-zA-Z0-9_]*)([.]([a-zA-Z_]+[a-zA-Z0-9_]*))*$"
