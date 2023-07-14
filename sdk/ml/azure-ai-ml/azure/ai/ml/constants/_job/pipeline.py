# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class PipelineConstants:
    DEFAULT_DATASTORE_SDK = "default_datastore_name"
    DEFAULT_DATASTORE_REST = "defaultDatastoreName"
    DEFAULT_DATASTORE = "default_datastore"
    DEFAULT_COMPUTE = "default_compute"
    CONTINUE_ON_STEP_FAILURE = "continue_on_step_failure"
    CONTINUE_RUN_ON_FAILED_OPTIONAL_INPUT = "continue_run_on_failed_optional_input"
    DATASTORE_REST = "Datastore"
    ENVIRONMENT = "environment"
    CODE = "code"
    REUSED_FLAG_FIELD = "azureml.isreused"
    REUSED_FLAG_TRUE = "true"
    REUSED_JOB_ID = "azureml.reusedrunid"
    PIPELINE_JOB_TYPE = "azureml.pipelinejob"


class ValidationErrorCode:
    PARAMETER_TYPE_UNKNOWN = "ParameterTypeUnknown"


# Methods in Python dictionary, when used as IO name, will actually get function rather than IO object,
# resulting in validation error.
# So print warning message on this and suggest user to access with syntax "d[key]" instead of "d.key".
# Reference: builtins.py::dict
COMPONENT_IO_KEYWORDS = {
    "clear",
    "copy",
    "fromkeys",
    "get",
    "items",
    "keys",
    "pop",
    "popitem",
    "setdefault",
    "update",
    "values",
    "__class_getitem__",
    "__contains__",
    "__delitem__",
    "__eq__",
    "__getattribute__",
    "__getitem__",
    "__ge__",
    "__init__",
    "__ior__",
    "__iter__",
    "__len__",
    "__le__",
    "__lt__",
    "__new__",
    "__ne__",
    "__or__",
    "__repr__",
    "__reversed__",
    "__ror__",
    "__setitem__",
    "__sizeof__",
    "__hash__",
}
