# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class PipelineConstants:
    DEFAULT_DATASTORE_SDK = "default_datastore_name"
    DEFAULT_DATASTORE_REST = "defaultDatastoreName"
    DEFAULT_DATASTORE = "default_datastore"
    DEFAULT_COMPUTE = "default_compute"
    CONTINUE_ON_STEP_FAILURE = "continue_on_step_failure"
    DATASTORE_REST = "Datastore"
    ENVIRONMENT = "environment"
    CODE = "code"
    REUSED_FLAG_FIELD = "azureml.isreused"
    REUSED_FLAG_TRUE = "true"
    REUSED_JOB_ID = "azureml.reusedrunid"


class ValidationErrorCode:
    PARAMETER_TYPE_UNKNOWN = "ParameterTypeUnknown"
