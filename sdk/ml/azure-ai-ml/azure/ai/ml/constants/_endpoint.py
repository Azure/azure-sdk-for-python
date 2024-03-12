# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class EndpointKeyType(object):
    PRIMARY_KEY_TYPE = "primary"
    SECONDARY_KEY_TYPE = "secondary"


class EndpointInvokeFields(object):
    DEFAULT_HEADER = {"Content-Type": "application/json"}
    AUTHORIZATION = "Authorization"
    MODEL_DEPLOYMENT = "azureml-model-deployment"
    REPEATABILITY_REQUEST_ID = "repeatability_request-id"


class EndpointGetLogsFields(object):
    LINES = 5000


class EndpointYamlFields(object):
    TYPE = "type"
    TRAFFIC_NAME = "traffic"
    NAME = "name"
    SCALE_SETTINGS = "scale_settings"
    SCALE_TYPE = "scale_type"
    INSTANCE_COUNT = "instance_count"
    MINIMUM = "min_instances"
    MAXIMUM = "max_instances"
    POLLING_INTERVAL = "polling_interval"
    TARGET_UTILIZATION_PERCENTAGE = "target_utilization_percentage"
    SKU_DEFAULT = "Standard_F4s_v2"
    COMPUTE = "compute"
    CODE_CONFIGURATION = "code_configuration"
    CODE = "code"
    SCORING_SCRIPT = "scoring_script"
    SCORING_URI = "scoring_uri"
    OPENAPI_URI = "openapi_uri"
    PROVISIONING_STATE = "provisioning_state"
    MINI_BATCH_SIZE = "mini_batch_size"
    RETRY_SETTINGS = "retry_settings"
    BATCH_JOB_INPUT_DATA = "input_data"
    BATCH_JOB_INSTANCE_COUNT = "compute.instance_count"
    BATCH_JOB_OUTPUT_DATA = "output_data"
    BATCH_JOB_OUTPUT_PATH = "output_dataset.path"
    BATCH_JOB_OUTPUT_DATSTORE = "output_dataset.datastore_id"
    BATCH_JOB_NAME = "job_name"
    BATCH_JOB_EXPERIMENT_NAME = "experiment_name"
    BATCH_JOB_PROPERTIES = "properties"


class EndpointConfigurations:
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 32
    NAME_REGEX_PATTERN = r"^[a-zA-Z]([-a-zA-Z0-9]*[a-zA-Z0-9])?$"


class LocalEndpointConstants:
    CONDA_FILE_NAME = "conda.yml"
    DOCKER_PORT = "5001"
    LABEL_KEY_AZUREML_LOCAL_ENDPOINT = "azureml-local-endpoint"
    LABEL_KEY_ENDPOINT_NAME = "endpoint"
    LABEL_KEY_DEPLOYMENT_NAME = "deployment"
    LABEL_KEY_ENDPOINT_JSON = "endpoint-data"
    LABEL_KEY_DEPLOYMENT_JSON = "deployment-data"
    LABEL_KEY_AZUREML_PORT = "azureml-port"
    DEFAULT_STARTUP_WAIT_TIME_SECONDS = 15
    CONTAINER_EXITED = "exited"
    ENDPOINT_STATE_FAILED = "Failed"
    ENDPOINT_STATE_SUCCEEDED = "Succeeded"
    ENDPOINT_STATE_LOCATION = "local"
    AZUREML_APP_PATH = "/var/azureml-app/"
    ENVVAR_KEY_AZUREML_ENTRY_SCRIPT = "AZUREML_ENTRY_SCRIPT"
    ENVVAR_KEY_AZUREML_MODEL_DIR = "AZUREML_MODEL_DIR"
    ENVVAR_KEY_AML_APP_ROOT = "AML_APP_ROOT"
    ENVVAR_KEY_AZUREML_INFERENCE_PYTHON_PATH = "AZUREML_INFERENCE_PYTHON_PATH"
    CONDA_ENV_NAME = "inf-conda-env"
    CONDA_ENV_BIN_PATH = "/opt/miniconda/envs/inf-conda-env/bin"
    CONDA_ENV_PYTHON_PATH = "/opt/miniconda/envs/inf-conda-env/bin/python"


class BatchEndpointInvoke:
    INPUTS = "inputs"
    OUTPUTS = "outputs"
    ENDPOINT = "endpoint"
    DEPLOYMENT = "deployment"
    TYPE = "type"
    MODE = "mode"
    PATH = "path"
    DEFAULT = "default"
    MIN = "min"
    MAX = "max"
