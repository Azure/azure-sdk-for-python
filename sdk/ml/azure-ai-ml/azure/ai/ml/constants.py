# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum


AZUREML_CLOUD_ENV_NAME = "AZUREML_CURRENT_CLOUD"
API_VERSION_2020_09_01_PREVIEW = "2020-09-01-preview"
API_VERSION_2020_09_01_DATAPLANE = "2020-09-01-dataplanepreview"
ONLINE_ENDPOINT_TYPE = "online"
BATCH_ENDPOINT_TYPE = "batch"
BASE_PATH_CONTEXT_KEY = "base_path"
PARAMS_OVERRIDE_KEY = "params_override"
TYPE = "type"
JOBLIMITSTYPE = "JobLimitsType"
DATA_ARM_TYPE = "data"
DATASET_ARM_TYPE = "datasets"
ARM_ID_PREFIX = "azureml:"
FILE_PREFIX = "file:"
FOLDER_PREFIX = "folder:"
HTTP_PREFIX = "http"
HTTPS_PREFIX = "https"
ARM_ID_FULL_PREFIX = "/subscriptions/"
AZUREML_RESOURCE_PROVIDER = "Microsoft.MachineLearningServices"
RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}"
NAMED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}/{}/{}"
LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/{}/{}"
VERSIONED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}/{}/{}/versions/{}"
DATASTORE_RESOURCE_ID = (
    "/subscriptions/{}/resourceGroups/{}/providers/" "Microsoft.MachineLearningServices/workspaces/{}/datastores/{}"
)
PROVIDER_RESOURCE_ID_WITH_VERSION = (
    "/subscriptions/{}/resourceGroups/{}/providers/" "Microsoft.MachineLearningServices/workspaces/{}/{}/{}/versions/{}"
)
ASSET_ID_FORMAT = "azureml://locations/{}/workspaces/{}/{}/{}/versions/{}"
VERSIONED_RESOURCE_NAME = "{}:{}"
PYTHON = "python"
AML_TOKEN_YAML = "aml_token"
AAD_TOKEN_YAML = "aad_token"
KEY = "key"
DEFAULT_ARM_RETRY_INTERVAL = 60
COMPONENT_TYPE = "type"
TID_FMT = "&tid={}"
AZUREML_PRIVATE_FEATURES_ENV_VAR = "AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED"
ENDPOINT_DEPLOYMENT_START_MSG = "{}/#blade/HubsExtension/DeploymentDetailsBlade/overview/id/%2Fsubscriptions%2F{}%2FresourceGroups%2F{}%2Fproviders%2FMicrosoft.Resources%2Fdeployments%2F{}\n"
AZUREML_LOCAL_ENDPOINTS_NOT_IMPLEMENTED_ERROR = "This operation for local endpoints is not supported yet."
BATCH_JOB_NOT_SUPPORTED_ERROR_CODE = "BatchJobNotSupported"
ENVIRONMENT_VARIABLES = "environment_variables"
LIMITED_RESULTSET_WARNING_FORMAT = "Displaying top {} results from the list command."
MAX_LIST_CLI_RESULTS = 50
LOCAL_COMPUTE_TARGET = "local"
LOCAL_COMPUTE_PROPERTY = "IsLocal"
CONDA_FILE = "conda_file"
DOCKER_FILE_NAME = "Dockerfile"
COMPUTE_UPDATE_ERROR = (
    "Only AmlCompute/KubernetesCompute cluster properties are supported, compute name {}, is {} type."
)
MAX_AUTOINCREMENT_ATTEMPTS = 3
REGISTRY_URI_REGEX_FORMAT = "azureml://registries/*"
REGISTRY_URI_FORMAT = "azureml://registries/"
REGISTRY_VERSION_PATTERN = "^azureml://registries/([^/]+)/([^/]+)/([^/]+)/versions/([^/]+)"
REGISTRY_ASSET_ID = "azureml://registries/{}/{}/{}/versions/{}"
SHORT_URI_FORMAT = "azureml://datastores/{}/paths/{}"
DATASTORE_SHORT_URI = "azureml://datastores/"
MLFLOW_URI_FORMAT = "runs:/{}/{}"
JOB_URI_FORMAT = "azureml://jobs/{}/outputs/{}/paths/{}"
LONG_URI_FORMAT = "azureml://subscriptions/{}/resourcegroups/{}/workspaces/{}/datastores/{}/paths/{}"
SHORT_URI_REGEX_FORMAT = "azureml://datastores/([^/]+)/paths/(.+)"
MLFLOW_URI_REGEX_FORMAT = "runs:/([^/?]+)/(.+)"
JOB_URI_REGEX_FORMAT = "azureml://jobs/([^/]+)/outputs/([^/]+)/paths/(.+)"
OUTPUT_URI_REGEX_FORMAT = "azureml://datastores/([^/]+)/(ExperimentRun/.+)"
LONG_URI_REGEX_FORMAT = (
    "azureml://subscriptions/([^/]+)/resource[gG]roups/([^/]+)/workspaces/([^/]+)/datastores/([^/]+)/paths/(.+)"
)
ASSET_ID_URI_REGEX_FORMAT = "azureml://locations/([^/]+)/workspaces/([^/]+)/([^/]+)/([^/]+)/versions/(.+)"
AZUREML_CLI_SYSTEM_EXECUTED_ENV_VAR = "AZUREML_CLI_SYSTEM_EXECUTED"
DOCSTRING_TEMPLATE = ".. note::" "    {0} {1}\n\n"
DOCSTRING_DEFAULT_INDENTATION = 8
EXPERIMENTAL_CLASS_MESSAGE = "This is an experimental class,"
EXPERIMENTAL_METHOD_MESSAGE = "This is an experimental method,"
EXPERIMENTAL_FIELD_MESSAGE = "This is an experimental field,"
EXPERIMENTAL_LINK_MESSAGE = (
    "and may change at any time. " "Please see https://aka.ms/azuremlexperimental for more information."
)
REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT = "For a more detailed breakdown of the {} schema, please see: {}."
STORAGE_AUTH_MISMATCH_ERROR = "AuthorizationPermissionMismatch"
SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME = "best_child_run_id"
BATCH_JOB_CHILD_RUN_NAME = "batchscoring"
BATCH_JOB_CHILD_RUN_OUTPUT_NAME = "score"
DEFAULT_ARTIFACT_STORE_OUTPUT_NAME = "default"

CREATE_ENVIRONMENT_ERROR_MESSAGE = "It looks like you are trying to specify a conda file for the --file/-f argument. --file/-f is reserved for the Azure ML Environment definition (see schema here: {}). To specify a conda file via command-line argument, please use --conda-file/-c argument."
API_URL_KEY = "api"
ANONYMOUS_ENV_NAME = "CliV2AnonymousEnvironment"
SKIP_VALIDATION_MESSAGE = "To skip this validation use the --skip-validation param"
MLTABLE_SCHEMA_URL_FALLBACK = "https://azuremlschemasprod.azureedge.net/latest/MLTable.schema.json"
STORAGE_ACCOUNT_URLS = {
    "AzureBlob": "https://{}.blob.{}",
    "AzureDataLakeGen2": "https://{}.dfs.{}",
    "AzureFile": "https://{}.file.{}",
}


class SearchSpace:
    # Hyperparameter search constants
    CHOICE = "choice"
    UNIFORM = "uniform"
    LOGUNIFORM = "loguniform"
    QUNIFORM = "quniform"
    QLOGUNIFORM = "qloguniform"
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
    QNORMAL = "qnormal"
    QLOGNORMAL = "qlognormal"
    RANDINT = "randint"

    UNIFORM_LOGUNIFORM = [UNIFORM, LOGUNIFORM]
    QUNIFORM_QLOGUNIFORM = [QUNIFORM, QLOGUNIFORM]
    NORMAL_LOGNORMAL = [NORMAL, LOGNORMAL]
    QNORMAL_QLOGNORMAL = [QNORMAL, QLOGNORMAL]


class DistributionType:
    MPI = "mpi"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"


class ComputeType(object):
    MANAGED = "managed"
    AMLCOMPUTE = "amlcompute"
    COMPUTEINSTANCE = "computeinstance"
    VIRTUALMACHINE = "virtualmachine"
    KUBERNETES = "kubernetes"


class ComputeTier(object):
    LOWPRIORITY = "low_priority"
    DEDICATED = "dedicated"


class IdentityType(object):
    SYSTEM_ASSIGNED = "system_assigned"
    USER_ASSIGNED = "user_assigned"
    BOTH = "system_assigned,user_assigned"


class DeploymentType(object):
    K8S = "Kubernetes"
    MANAGED = "Managed"


class EndpointDeploymentLogContainerType(object):
    STORAGE_INITIALIZER_REST = "StorageInitializer"
    INFERENCE_SERVER_REST = "InferenceServer"
    INFERENCE_SERVER = "inference-server"
    STORAGE_INITIALIZER = "storage-initializer"


class EndpointKeyType(object):
    PRIMARY_KEY_TYPE = "primary"
    SECONDARY_KEY_TYPE = "secondary"


class JobType(object):
    COMMAND = "command"
    SWEEP = "sweep"
    PIPELINE = "pipeline"
    AUTOML = "automl"
    COMPONENT = "component"
    BASE = "base"
    PARALLEL = "parallel"


class JobLimitsType(object):
    SWEEP = "Sweep"


class JobLogPattern:
    COMMAND_JOB_LOG_PATTERN = "azureml-logs/[\\d]{2}.+\\.txt"
    PIPELINE_JOB_LOG_PATTERN = "logs/azureml/executionlogs\\.txt"
    SWEEP_JOB_LOG_PATTERN = "azureml-logs/hyperdrive\\.txt"
    COMMON_RUNTIME_STREAM_LOG_PATTERN = "user_logs/std_log[\\D]*[0]*(?:_ps)?\\.txt"
    COMMON_RUNTIME_ALL_USER_LOG_PATTERN = "user_logs/std_log.*\\.txt"


class JobServices:
    STUDIO = "Studio"


class AzureMLResourceType(object):
    CODE = "codes"
    COMPUTE = "computes"
    DATA = "data"
    DATASET = "datasets"
    DATASTORE = "datastores"
    ONLINE_ENDPOINT = "online_endpoints"
    BATCH_ENDPOINT = "batch_endpoints"
    ONLINE_DEPLOYMENT = "online_deployments"
    DEPLOYMENT = "deployments"
    BATCH_DEPLOYMENT = "batch_deployments"
    ENVIRONMENT = "environments"
    JOB = "jobs"
    MODEL = "models"
    VIRTUALCLUSTER = "virtualclusters"
    WORKSPACE = "workspaces"
    WORKSPACE_CONNECTION = "workspace_connections"
    COMPONENT = "components"

    NAMED_TYPES = {
        JOB,
        COMPUTE,
        WORKSPACE,
        ONLINE_ENDPOINT,
        ONLINE_DEPLOYMENT,
        DATASTORE,
    }
    VERSIONED_TYPES = {MODEL, DATA, DATASET, CODE, ENVIRONMENT, COMPONENT}


class ArmConstants(object):
    CODE_PARAMETER_NAME = "codes"
    CODE_VERSION_PARAMETER_NAME = "codeVersions"
    MODEL_PARAMETER_NAME = "models"
    MODEL_VERSION_PARAMETER_NAME = "modelVersions"
    ENVIRONMENT_PARAMETER_NAME = "environments"
    WORKSPACE_PARAMETER_NAME = "workspaceName"
    LOCATION_PARAMETER_NAME = "location"
    ENDPOINT_IDENTITY_PARAMETER_NAME = "onlineEndpointIdentity"
    ENDPOINT_PARAMETER_NAME = "onlineEndpoint"
    ENDPOINT_PROPERTIES_PARAMETER_NAME = "onlineEndpointProperties"
    ENDPOINT_PROPERTIES_TRAFFIC_UPDATE_PARAMETER_NAME = "onlineEndpointPropertiesTrafficUpdate"
    ENDPOINT_NAME_PARAMETER_NAME = "onlineEndpointName"
    ENDPOINT_TAGS_PARAMETER_NAME = "onlineEndpointTags"
    DEPLOYMENTS_PARAMETER_NAME = "onlineDeployments"
    PROPERTIES_PARAMETER_NAME = "properties"
    DEPENDSON_PARAMETER_NAME = "dependsOn"
    TRAFFIC_PARAMETER_NAME = "trafficRules"
    CODE_RESOURCE_NAME = "codeDeploymentCopy"
    CODE_VERSION_RESOURCE_NAME = "codeVersionDeploymentCopy"
    MODEL_RESOURCE_NAME = "modelDeploymentCopy"
    MODEL_VERSION_RESOURCE_NAME = "modelVersionDeploymentCopy"
    ENVIRONMENT_VERSION_RESOURCE_NAME = "environmentVersionDeploymentCopy"
    ONLINE_DEPLOYMENT_RESOURCE_NAME = "onlineDeploymentCopy"
    ONLINE_ENDPOINT_RESOURCE_NAME = "onlineEndpointCopy"
    UPDATE_RESOURCE_NAME = "updateEndpointWithTraffic"
    ENDPOINT_CREATE_OR_UPDATE_PARAMETER_NAME = "endpointCreateOrUpdate"
    TAGS = "tags"
    SKU = "sku"
    KEY_VAULT_PARAMETER_NAME = "vaults"
    STORAGE_ACCOUNT_PARAMETER_NAME = "storageAccounts"
    APP_INSIGHTS_PARAMETER_NAME = "components"
    CONTAINER_REGISTRY_PARAMETER_NAME = "registries"

    CODE_TYPE = "code"
    CODE_VERSION_TYPE = "code_version"
    MODEL_TYPE = "model"
    MODEL_VERSION_TYPE = "model_version"
    ENVIRONMENT_TYPE = "environment"
    ENVIRONMENT_VERSION_TYPE = "environment_version"
    ONLINE_ENDPOINT_TYPE = "online_endpoint"
    ONLINE_DEPLOYMENT_TYPE = "online_deployment"
    UPDATE_ONLINE_ENDPOINT_TYPE = "update_online_endpoint"
    BASE_TYPE = "base"
    WORKSPACE_BASE = "workspace_base"
    WORKSPACE_PARAM = "workspace_param"

    OPERATION_CREATE = "create"
    OPERATION_UPDATE = "update"
    NAME = "name"
    VERSION = "version"
    ASSET_PATH = "assetPath"
    DATASTORE_ID = "datastoreId"
    OBJECT = "Object"
    ARRAY = "Array"
    STRING = "String"
    DEFAULT_VALUE = "defaultValue"

    STORAGE = "StorageAccount"
    KEY_VAULT = "KeyVault"
    APP_INSIGHTS = "AppInsights"
    WORKSPACE = "Workspace"

    AZURE_MGMT_RESOURCE_API_VERSION = "2020-06-01"
    AZURE_MGMT_STORAGE_API_VERSION = "2019-06-01"
    AZURE_MGMT_APPINSIGHT_API_VERSION = "2015-05-01"
    AZURE_MGMT_KEYVAULT_API_VERSION = "2019-09-01"
    AZURE_MGMT_CONTAINER_REG_API_VERSION = "2019-05-01"


class WorkspaceResourceConstants(object):
    ENCRYPTION_STATUS_ENABLED = "Enabled"


class HttpResponseStatusCode(object):
    NOT_FOUND = 404


class OperationStatus(object):
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELED = "Canceled"
    RUNNING = "Running"


class EndpointInvokeFields(object):
    DEFAULT_HEADER = {"Content-Type": "application/json"}
    AUTHORIZATION = "Authorization"
    MODEL_DEPLOYMENT = "azureml-model-deployment"


class EndpointGetLogsFields(object):
    LINES = 5000


class CommonYamlFields(object):
    TYPE = "type"


class JobComputePropertyFields(object):
    # Legacy name
    AISUPERCOMPUTER = "AISuperComputer"
    SINGULARITY = "Singularity"


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
    SWAGGER_URI = "swagger_uri"
    PROVISIONING_STATE = "provisioning_state"
    MINI_BATCH_SIZE = "mini_batch_size"
    RETRY_SETTINGS = "retry_settings"
    BATCH_JOB_INPUT_DATA = "input_data"
    BATCH_JOB_INSTANCE_COUNT = "compute.instance_count"
    BATCH_JOB_OUTPUT_PATH = "output_dataset.path"
    BATCH_JOB_OUTPUT_DATSTORE = "output_dataset.datastore_id"
    BATCH_JOB_DATASET = "dataset"
    BATCH_JOB_NAME = "job_name"


class GitProperties(object):
    ENV_REPOSITORY_URI = "AZUREML_GIT_REPOSITORY_URI"
    ENV_BRANCH = "AZUREML_GIT_BRANCH"
    ENV_COMMIT = "AZUREML_GIT_COMMIT"
    ENV_DIRTY = "AZUREML_GIT_DIRTY"
    ENV_BUILD_ID = "AZUREML_GIT_BUILD_ID"
    ENV_BUILD_URI = "AZUREML_GIT_BUILD_URI"

    PROP_DIRTY = "azureml.git.dirty"
    PROP_BUILD_ID = "azureml.git.build_id"
    PROP_BUILD_URI = "azureml.git.build_uri"

    PROP_MLFLOW_GIT_BRANCH = "mlflow.source.git.branch"
    PROP_MLFLOW_GIT_COMMIT = "mlflow.source.git.commit"
    PROP_MLFLOW_GIT_REPO_URL = "mlflow.source.git.repoURL"


class AutoMLConstants:
    # The following are fields found in the yaml for AutoML Job
    GENERAL_YAML = "general"
    DATA_YAML = "data"
    FEATURIZATION_YAML = "featurization"
    LIMITS_YAML = "limits"
    SWEEP_YAML = "sweep"
    FORECASTING_YAML = "forecasting"
    TRAINING_YAML = "training"
    MAX_TRIALS_YAML = "max_trials"
    DATASET_YAML = "dataset"
    VALIDATION_DATASET_SIZE_YAML = "validation_dataset_size"
    TRAINING_DATA_SETTINGS_YAML = "training"
    TEST_DATA_SETTINGS_YAML = "test"
    VALIDATION_DATA_SETTINGS_YAML = "validation"
    COUNTRY_OR_REGION_YAML = "country_or_region_for_holidays"
    TASK_TYPE_YAML = "task"
    TIMEOUT_YAML = "timeout_minutes"
    TRIAL_TIMEOUT_YAML = "trial_timeout_minutes"
    BLOCKED_ALGORITHMS_YAML = "blocked_training_algorithms"
    ALLOWED_ALGORITHMS_YAML = "allowed_training_algorithms"
    ENSEMBLE_MODEL_DOWNLOAD_TIMEOUT_YAML = "ensemble_model_download_timeout_minutes"
    TERMINATION_POLICY_TYPE_YAML = "type"

    # TASK TYPES
    CLASSIFICATION_YAML = "classification"
    REGRESSION_YAML = "regression"
    FORECASTING_YAML = "forecasting"

    # The following are general purpose AutoML fields
    TARGET_LAGS = "target_lags"
    AUTO = "auto"
    OFF = "off"
    CUSTOM = "custom"
    TIME_SERIES_ID_COLUMN_NAMES = "time_series_id_column_names"
    TRANSFORMER_PARAMS = "transformer_params"
    MODE = "mode"


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


class OnlineEndpointConfigurations:
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 32
    NAME_REGEX_PATTERN = r"^[a-zA-Z]([-a-zA-Z0-9]*[a-zA-Z0-9])?$"


class LROConfigurations:
    MAX_WAIT_COUNT = 400
    POLLING_TIMEOUT = 720
    POLL_INTERVAL = 5
    SLEEP_TIME = 5


class OrderString:
    CREATED_AT = "createdtime asc"
    CREATED_AT_DESC = "createdtime desc"


class ComputeDefaults:
    VMSIZE = "STANDARD_DS3_V2"
    ADMIN_USER = "azureuser"
    MIN_NODES = 0
    MAX_NODES = 4
    IDLE_TIME = 1800
    PRIORITY = "Dedicated"


class ComponentJobConstants(object):
    INPUT_PATTERN = r"^\$\{\{parent\.(inputs|jobs)\.(.*?)\}\}$"
    OUTPUT_PATTERN = r"^\$\{\{parent\.outputs\.(.*?)\}\}$"
    LEGACY_INPUT_PATTERN = r"^\$\{\{(inputs|jobs)\.(.*?)\}\}$"
    LEGACY_OUTPUT_PATTERN = r"^\$\{\{outputs\.(.*?)\}\}$"
    INPUT_DESTINATION_FORMAT = "jobs.{}.inputs.{}"
    OUTPUT_DESTINATION_FORMAT = "jobs.{}.outputs.{}"


class DockerTypes:
    IMAGE = "Image"
    BUILD = "Build"


class DataType:
    SIMPLE = "Simple"
    DATAFLOW = "Dataflow"


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


class InputOutputModes:
    MOUNT = "mount"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    RO_MOUNT = "ro_mount"
    RW_MOUNT = "rw_mount"
    EVAL_MOUNT = "eval_mount"
    EVAL_DOWNLOAD = "eval_download"
    DIRECT = "direct"


class LegacyAssetTypes:
    PATH = "path"


class AssetTypes:
    URI_FILE = "uri_file"
    URI_FOLDER = "uri_folder"
    MLTABLE = "mltable"
    MLFLOW_MODEL = "mlflow_model"
    TRITON_MODEL = "triton_model"
    CUSTOM_MODEL = "custom_model"


class BatchDeploymentOutputAction:
    APPEND_ROW = "append_row"
    SUMMARY_ONLY = "summary_only"


class PublicNetworkAccess:
    ENABLED = "Enabled"
    DISABLED = "Disabled"


class ModelType:
    CUSTOM = "CustomModel"
    MLFLOW = "MLFlowModel"
    TRITON = "TritonModel"


class YAMLRefDocLinks:
    WORKSPACE = "https://aka.ms/ml-cli-v2-workspace-yaml-reference"
    ENVIRONMENT = "https://aka.ms/ml-cli-v2-environment-yaml-reference"
    DATASET = "https://aka.ms/ml-cli-v2-dataset-yaml-reference"
    DATA = "https://aka.ms/ml-cli-v2-data-yaml-reference"
    MODEL = "https://aka.ms/ml-cli-v2-model-yaml-reference"
    AML_COMPUTE = "https://aka.ms/ml-cli-v2-compute-aml-yaml-reference"
    COMPUTE_INSTANCE = "https://aka.ms/ml-cli-v2-compute-aml-yaml-reference"
    VIRTUAL_MACHINE_COMPUTE = "https://aka.ms/ml-cli-v2-compute-vm-yaml-reference"
    COMMAND_JOB = "https://aka.ms/ml-cli-v2-job-command-yaml-reference"
    PARALLEL_JOB = "https://aka.ms/ml-cli-v2-job-parallel-yaml-reference"
    SWEEP_JOB = "https://aka.ms/ml-cli-v2-job-sweep-yaml-reference"
    PIPELINE_JOB = "https://aka.ms/ml-cli-v2-job-pipeline-yaml-reference"
    DATASTORE_BLOB = "https://aka.ms/ml-cli-v2-datastore-blob-yaml-reference"
    DATASTORE_FILE = "https://aka.ms/ml-cli-v2-datastore-file-yaml-reference"
    DATASTORE_DATA_LAKE_GEN_1 = "https://aka.ms/ml-cli-v2-datastore-data-lake-gen1-yaml-reference"
    DATASTORE_DATA_LAKE_GEN_2 = "https://aka.ms/ml-cli-v2-datastore-data-lake-gen2-yaml-reference"
    ONLINE_ENDPOINT = "https://aka.ms/ml-cli-v2-endpoint-online-yaml-reference"
    BATCH_ENDPOINT = "https://aka.ms/ml-cli-v2-endpoint-batch-yaml-reference"
    MANAGED_ONLINE_DEPLOYMENT = "https://aka.ms/ml-cli-v2-deployment-managed-online-yaml-reference"
    KUBERNETES_ONLINE_DEPLOYMENT = "https://aka.ms/ml-cli-v2-deployment-kubernetes-online-yaml-reference"
    BATCH_DEPLOYMENT = "https://aka.ms/ml-cli-v2-deployment-batch-yaml-reference"
    COMMAND_COMPONENT = "https://aka.ms/ml-cli-v2-component-command-yaml-reference"
    PARALLEL_COMPONENT = "https://aka.ms/ml-cli-v2-component-parallel-yaml-reference"


class YAMLRefDocSchemaNames:
    WORKSPACE = "Workspace"
    ENVIRONMENT = "Environment"
    DATA = "Data"
    DATASET = "Dataset"
    MODEL = "Model"
    AML_COMPUTE = "AMLCompute"
    COMPUTE_INSTANCE = "ComputeInstance"
    VIRTUAL_MACHINE_COMPUTE = "VirtualMachineCompute"
    COMMAND_JOB = "CommandJob"
    SWEEP_JOB = "SweepJob"
    PARALLEL_JOB = "ParallelJob"
    PIPELINE_JOB = "PipelineJob"
    DATASTORE_BLOB = "AzureBlobDatastore"
    DATASTORE_FILE = "AzureFileDatastore"
    DATASTORE_DATA_LAKE_GEN_1 = "AzureDataLakeGen1Datastore"
    DATASTORE_DATA_LAKE_GEN_2 = "AzureDataLakeGen2Datastore"
    ONLINE_ENDPOINT = "OnlineEndpoint"
    BATCH_ENDPOINT = "BatchEndpoint"
    MANAGED_ONLINE_DEPLOYMENT = "ManagedOnlineDeployment"
    KUBERNETES_ONLINE_DEPLOYMENT = "KubernetesOnlineDeployment"
    BATCH_DEPLOYMENT = "BatchDeployment"
    COMMAND_COMPONENT = "CommandComponent"
    PARALLEL_COMPONENT = "ParallelComponent"


class NodeType(object):
    COMMAND = "command"
    SWEEP = "sweep"
    PARALLEL = "parallel"
    AUTOML = "automl"


class ComponentSource:
    """Indicate where the component is constructed."""

    BUILDER = "BUILDER"
    DSL = "DSL"
    SDK = "SDK"
    REST = "REST"
    YAML = "YAML"


class LoggingLevel:
    WARN = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class ParallelTaskType:
    FUNCTION = "function"
    MODEL = "model"


class TimeZone(str, Enum):
    "Time zones that a job or compute instance schedule accepts"

    DATELINE_STANDARD_TIME = "Dateline Standard Time"
    UTC_11 = "UTC-11"
    ALEUTIAN_STANDARD_TIME = "Aleutian Standard Time"
    HAWAIIAN_STANDARD_TIME = "Hawaiian Standard Time"
    MARQUESAS_STANDARD_TIME = "Marquesas Standard Time"
    ALASKAN_STANDARD_TIME = "Alaskan Standard Time"
    UTC_09 = "UTC-09"
    PACIFIC_STANDARD_TIME_MEXICO = "Pacific Standard Time (Mexico)"
    UTC_08 = "UTC-08"
    PACIFIC_STANDARD_TIME = "Pacific Standard Time"
    US_MOUNTAIN_STANDARD_TIME = "US Mountain Standard Time"
    MOUNTAIN_STANDARD_TIME_MEXICO = "Mountain Standard Time (Mexico)"
    MOUNTAIN_STANDARD_TIME = "Mountain Standard Time"
    CENTRAL_AMERICA_STANDARD_TIME = "Central America Standard Time"
    CENTRAL_STANDARD_TIME = "Central Standard Time"
    EASTER_ISLAND_STANDARD_TIME = "Easter Island Standard Time"
    CENTRAL_STANDARD_TIME_MEXICO = "Central Standard Time (Mexico)"
    CANADA_CENTRAL_STANDARD_TIME = "Canada Central Standard Time"
    SA_PACIFIC_STANDARD_TIME = "SA Pacific Standard Time"
    EASTERN_STANDARD_TIME_MEXICO = "Eastern Standard Time (Mexico)"
    EASTERN_STANDARD_TIME = "Eastern Standard Time"
    HAITI_STANDARD_TIME = "Haiti Standard Time"
    CUBA_STANDARD_TIME = "Cuba Standard Time"
    US_EASTERN_STANDARD_TIME = "US Eastern Standard Time"
    PARAGUAY_STANDARD_TIME = "Paraguay Standard Time"
    ATLANTIC_STANDARD_TIME = "Atlantic Standard Time"
    VenezuelaStandardTime = "Venezuela Standard Time"
    CENTRAL_BRAZILIAN_STANDARD_TIME = "Central Brazilian Standard Time"
    SA_WESTERN_STANDARD_TIME = "SA Western Standard Time"
    PACIFIC_SA_STANDARD_TIME = "Pacific SA Standard Time"
    TURKS_AND_CAICOS_STANDARD_TIME = "Turks And Caicos Standard Time"
    NEWFOUNDLAND_STANDARD_TIME = "Newfoundland Standard Time"
    TOCANTINS_STANDARD_TIME = "Tocantins Standard Time"
    E_SOUTH_AMERICAN_STANDARD_TIME = "E. South America Standard Time"
    SA_EASTERN_STANDARD_TIME = "SA Eastern Standard Time"
    ARGENTINA_STANDARD_TIME = "Argentina Standard Time"
    GREENLAND_STANDARD_TIME = "Greenland Standard Time"
    MONTEVIDEO_STANDARD_TIME = "Montevideo Standard Time"
    SAINT_PIERRE_STANDARD_TIME = "Saint Pierre Standard Time"
    BAHIA_STANDARD_TIME = "Bahia Standard Time"
    UTC_02 = "UTC-02"
    MID_ATLANTIC_STANDARD_TIME = "Mid-Atlantic Standard Time"
    AZORES_STANDARD_TIME = "Azores Standard Time"
    CAPE_VERDE_STANDARD_TIME = "Cape Verde Standard Time"
    UTC = "UTC"
    MOROCCO_STANDARD_TIME = "Morocco Standard Time"
    GMT_STANDARD_TIME = "GMT Standard Time"
    GREENWICH_STANDARD_TIME = "Greenwich Standard Time"
    W_EUROPE_STANDARD_TIME = "W. Europe Standard Time"
    CENTRAL_EUROPE_STANDARD_TIME = "Central Europe Standard Time"
    ROMANCE_STANDARD_TIME = "Romance Standard Time"
    CENTRAL_EUROPEAN_STANDARD_TIME = "Central European Standard Time"
    W_CENTEAL_AFRICA_STANDARD_TIME = "W. Central Africa Standard Time"
    NAMIBIA_STANDARD_TIME = "Namibia Standard Time"
    JORDAN_STANDARD_TIME = "Jordan Standard Time"
    GTB_STANDARD_TIME = "GTB Standard Time"
    MIDDLE_EAST_STANDARD_TIME = "Middle East Standard Time"
    EGYPT_STANDARD_TIME = "Egypt Standard Time"
    E_EUROPE_STANDARD_TIME = "E. Europe Standard Time"
    SYRIA_STANDARD_TIME = "Syria Standard Time"
    WEST_BANK_STANDARD_TIME = "West Bank Standard Time"
    SOUTH_AFRICA_STANDARD_TIME = "South Africa Standard Time"
    FLE_STANDARD_TIME = "FLE Standard Time"
    TURKEY_STANDARD_TIME = "Turkey Standard Time"
    ISRAEL_STANDARD_TIME = "Israel Standard Time"
    KALININGRAD_STANDARD_TIME = "Kaliningrad Standard Time"
    LIBYA_STANDARD_TIME = "Libya Standard Time"
    ARABIC_STANDARD_TIME = "Arabic Standard Time"
    ARAB_STANDARD_TIME = "Arab Standard Time"
    BELARUS_STANDARD_TIME = "Belarus Standard Time"
    RUSSIAN_STANDARD_TIME = "Russian Standard Time"
    E_AFRICA_STANDARD_TIME = "E. Africa Standard Time"
    IRAN_STANDARD_TIME = "Iran Standard Time"
    ARABIAN_STANDARD_TIME = "Arabian Standard Time"
    ASTRAKHAN_STANDARD_TIME = "Astrakhan Standard Time"
    AZERBAIJAN_STANDARD_TIME = "Azerbaijan Standard Time"
    RUSSIA_TIME_ZONE_3 = "Russia Time Zone 3"
    MAURITIUS_STANDARD_TIME = "Mauritius Standard Time"
    GEORGIAN_STANDARD_TIME = "Georgian Standard Time"
    CAUCASUS_STANDARD_TIME = "Caucasus Standard Time"
    AFGHANISTANA_STANDARD_TIME = "Afghanistan Standard Time"
    WEST_ASIA_STANDARD_TIME = "West Asia Standard Time"
    EKATERINBURG_STANDARD_TIME = "Ekaterinburg Standard Time"
    PAKISTAN_STANDARD_TIME = "Pakistan Standard Time"
    INDIA_STANDARD_TIME = "India Standard Time"
    SRI_LANKA_STANDARD_TIME = "Sri Lanka Standard Time"
    NEPAL_STANDARD_TIME = "Nepal Standard Time"
    CENTRAL_ASIA_STANDARD_TIME = "Central Asia Standard Time"
    BANGLADESH_STANDARD_TIME = "Bangladesh Standard Time"
    N_CENTRAL_ASIA_STANDARD_TIME = "N. Central Asia Standard Time"
    MYANMAR_STANDARD_TIME = "Myanmar Standard Time"
    SE_ASIA_STANDARD_TIME = "SE Asia Standard Time"
    ALTAI_STANDARD_TIME = "Altai Standard Time"
    W_MONGOLIA_STANDARD_TIME = "W. Mongolia Standard Time"
    NORTH_ASIA_STANDARD_TIME = "North Asia Standard Time"
    TOMSK_STANDARD_TIME = "Tomsk Standard Time"
    CHINA_STANDARD_TIME = "China Standard Time"
    NORTH_ASIA_EAST_STANDARD_TIME = "North Asia East Standard Time"
    SINGAPORE_STANDARD_TIME = "Singapore Standard Time"
    W_AUSTRALIA_STANDARD_TIME = "W. Australia Standard Time"
    TAIPEI_STANDARD_TIME = "Taipei Standard Time"
    ULAANBAATAR_STANDARD_TIME = "Ulaanbaatar Standard Time"
    NORTH_KOREA_STANDARD_TIME = "North Korea Standard Time"
    AUS_CENTRAL_W_STANDARD_TIME = "Aus Central W. Standard Time"
    TRANSBAIKAL_STANDARD_TIME = "Transbaikal Standard Time"
    TOKYO_STANDARD_TIME = "Tokyo Standard Time"
    KOREA_STANDARD_TIME = "Korea Standard Time"
    YAKUTSK_STANDARD_TIME = "Yakutsk Standard Time"
    CEN_AUSTRALIA_STANDARD_TIME = "Cen. Australia Standard Time"
    AUS_CENTRAL_STANDARD_TIME = "AUS Central Standard Time"
    E_AUSTRALIAN_STANDARD_TIME = "E. Australia Standard Time"
    AUS_EASTERN_STANDARD_TIME = "AUS Eastern Standard Time"
    WEST_PACIFIC_STANDARD_TIME = "West Pacific Standard Time"
    TASMANIA_STANDARD_TIME = "Tasmania Standard Time"
    VLADIVOSTOK_STANDARD_TIME = "Vladivostok Standard Time"
    LORDE_HOWE_STANDARD_TIME = "Lord Howe Standard Time"
    BOUGAINVILLE_STANDARD_TIME = "Bougainville Standard Time"
    RUSSIA_TIME_ZONE_10 = "Russia Time Zone 10"
    MAGADAN_STANDARD_TIME = "Magadan Standard Time"
    NORFOLK_STANDARD_TIME = "Norfolk Standard Time"
    SAKHALIN_STANDARD_TIME = "Sakhalin Standard Time"
    CENTRAL_PACIFIC_STANDARD_TIME = "Central Pacific Standard Time"
    RUSSIA_TIME_ZONE_11 = "Russia Time Zone 11"
    NEW_ZEALAND_STANDARD_TIME = "New Zealand Standard Time"
    UTC_12 = "UTC+12"
    FIJI_STANDARD_TIME = "Fiji Standard Time"
    KAMCHATKA_STANDARD_TIME = "Kamchatka Standard Time"
    CHATHAM_ISLANDS_STANDARD_TIME = "Chatham Islands Standard Time"
    TONGA__STANDARD_TIME = "Tonga Standard Time"
    SAMOA_STANDARD_TIME = "Samoa Standard Time"
    LINE_ISLANDS_STANDARD_TIME = "Line Islands Standard Time"
