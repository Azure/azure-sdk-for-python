# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta

AZUREML_CLOUD_ENV_NAME = "AZUREML_CURRENT_CLOUD"
API_VERSION_2020_09_01_PREVIEW = "2020-09-01-preview"
API_VERSION_2020_09_01_DATAPLANE = "2020-09-01-dataplanepreview"
ONLINE_ENDPOINT_TYPE = "online"
BATCH_ENDPOINT_TYPE = "batch"
BASE_PATH_CONTEXT_KEY = "base_path"
SOURCE_PATH_CONTEXT_KEY = "source_path"
PARAMS_OVERRIDE_KEY = "params_override"
TYPE = "type"
JOBLIMITSTYPE = "JobLimitsType"
DATA_ARM_TYPE = "data"
ARM_ID_PREFIX = "azureml:"
CURATED_ENV_PREFIX = "AzureML-"
FILE_PREFIX = "file:"
FOLDER_PREFIX = "folder:"
HTTP_PREFIX = "http"
HTTPS_PREFIX = "https"
ARM_ID_FULL_PREFIX = "/subscriptions/"
AZUREML_RESOURCE_PROVIDER = "Microsoft.MachineLearningServices"
RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}"
NAMED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}/{}/{}"
NAMED_RESOURCE_ID_FORMAT_WITH_PARENT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}/{}/{}/{}/{}"
LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/{}/{}"
VERSIONED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}/{}/{}/versions/{}"
LABELLED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}/{}/{}/labels/{}"
DATASTORE_RESOURCE_ID = (
    "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/datastores/{}"
)
PROVIDER_RESOURCE_ID_WITH_VERSION = (
    "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/{}/{}/versions/{}"
)
SINGULARITY_ID_FORMAT = (
    "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/virtualclusters/{}"
)
SINGULARITY_ID_REGEX_FORMAT = (
    "/subscriptions/.*/resourceGroups/.*/providers/Microsoft.MachineLearningServices/virtualclusters/.*"
)
SINGULARITY_FULL_NAME_REGEX_FORMAT = (
    "^(azureml:)?//subscriptions/(?P<subscription_id>[^/]+)/resourceGroups/(?P<resource_group_name>[^/]+)/"
    "virtualclusters/(?P<name>[^/]+)"
)
SINGULARITY_SHORT_NAME_REGEX_FORMAT = "^(azureml:)?//virtualclusters/(?P<name>[^/]+)"
ASSET_ID_FORMAT = "azureml://locations/{}/workspaces/{}/{}/{}/versions/{}"
VERSIONED_RESOURCE_NAME = "{}:{}"
LABELLED_RESOURCE_NAME = "{}@{}"
LABEL_SPLITTER = "@"
PYTHON = "python"
AML_TOKEN_YAML = "aml_token"
AAD_TOKEN_YAML = "aad_token"
KEY = "key"
DEFAULT_ARM_RETRY_INTERVAL = 60
COMPONENT_TYPE = "type"
TID_FMT = "&tid={}"
AZUREML_PRIVATE_FEATURES_ENV_VAR = "AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED"
AZUREML_INTERNAL_COMPONENTS_ENV_VAR = "AZURE_ML_INTERNAL_COMPONENTS_ENABLED"
AZUREML_DISABLE_ON_DISK_CACHE_ENV_VAR = "AZURE_ML_DISABLE_ON_DISK_CACHE"
AZUREML_COMPONENT_REGISTRATION_MAX_WORKERS = "AZURE_ML_COMPONENT_REGISTRATION_MAX_WORKERS"
AZUREML_DISABLE_CONCURRENT_COMPONENT_REGISTRATION = "AZURE_ML_DISABLE_CONCURRENT_COMPONENT_REGISTRATION"
AZUREML_INTERNAL_COMPONENTS_SCHEMA_PREFIX = "https://componentsdk.azureedge.net/jsonschema/"
COMMON_RUNTIME_ENV_VAR = "AZUREML_COMPUTE_USE_COMMON_RUNTIME"
ENDPOINT_DEPLOYMENT_START_MSG = (
    "{}/#blade/HubsExtension/DeploymentDetailsBlade/overview/id/"
    "%2Fsubscriptions%2F{}%2FresourceGroups%2F{}%2Fproviders%2FMicrosoft.Resources%2Fdeployments%2F{}\n"
)
AZUREML_LOCAL_ENDPOINTS_NOT_IMPLEMENTED_ERROR = "This operation for local endpoints is not supported yet."
BATCH_JOB_NOT_SUPPORTED_ERROR_CODE = "BatchJobNotSupported"
ENVIRONMENT_VARIABLES = "environment_variables"
LIMITED_RESULTSET_WARNING_FORMAT = "Displaying top {} results from the list command."
MAX_LIST_CLI_RESULTS = 50
LOCAL_COMPUTE_TARGET = "local"
LOCAL_COMPUTE_PROPERTY = "IsLocal"
SERVERLESS_COMPUTE = "serverless"
CONDA_FILE = "conda_file"
DOCKER_FILE_NAME = "Dockerfile"
COMPUTE_UPDATE_ERROR = (
    "Only AmlCompute/KubernetesCompute cluster properties are supported, compute name {}, is {} type."
)
MAX_AUTOINCREMENT_ATTEMPTS = 3
REGISTRY_URI_REGEX_FORMAT = "azureml://registries/*"
REGISTRY_URI_FORMAT = "azureml://registries/"
INTERNAL_REGISTRY_URI_FORMAT = "azureml://feeds/"
REGISTRY_VERSION_PATTERN = "^azureml://registries/([^/]+)/([^/]+)/([^/]+)/versions/([^/]+)"
REGISTRY_ASSET_ID = "azureml://registries/{}/{}/{}/versions/{}"
SHORT_URI_FORMAT = "azureml://datastores/{}/paths/{}"
DATASTORE_SHORT_URI = "azureml://datastores/"
MLFLOW_URI_FORMAT = "runs:/{}/{}"
JOB_URI_FORMAT = "azureml://jobs/{}/outputs/{}/paths/{}"
LONG_URI_FORMAT = "azureml://subscriptions/{}/resourcegroups/{}/workspaces/{}/datastores/{}/paths/{}"
SHORT_URI_REGEX_FORMAT = "azureml://datastores/([^/]+)/paths/(.+)"
MLFLOW_URI_REGEX_FORMAT = "runs:/([^/?]+)/(.+)"
AZUREML_REGEX_FORMAT = "azureml:([^/]+):(.+)"
JOB_URI_REGEX_FORMAT = "azureml://jobs/([^/]+)/outputs/([^/]+)/paths/(.+)"
OUTPUT_URI_REGEX_FORMAT = "azureml://datastores/([^/]+)/(ExperimentRun/.+)"
LONG_URI_REGEX_FORMAT = (
    "azureml://subscriptions/([^/]+)/resource[gG]roups/([^/]+)/workspaces/([^/]+)/datastores/([^/]+)/paths/(.+)"
)
ASSET_ARM_ID_REGEX_FORMAT = (
    "azureml:/subscriptions/([^/]+)/resource[gG]roups/([^/]+)/"
    "providers/Microsoft.MachineLearningServices/workspaces/([^/]+)/([^/]+)/([^/]+)/versions/(.+)"
)
ASSET_ID_REGEX_FORMAT = (
    "azureml://subscriptions/([^/]+)/resource[gG]roups/([^/]+)/workspaces/([^/]+)/([^/]+)/([^/]+)/versions/(.+)"
)
ASSET_ID_RESOURCE_REGEX_FORMAT = "azureml://resource[gG]roups/([^/]+)/workspaces/([^/]+)/([^/]+)/([^/]+)/versions/(.+)"
MODEL_ID_REGEX_FORMAT = "azureml://models/([^/]+)/versions/(.+)"
DATA_ID_REGEX_FORMAT = "azureml://data/([^/]+)/versions/(.+)"
ASSET_ID_URI_REGEX_FORMAT = "azureml://locations/([^/]+)/workspaces/([^/]+)/([^/]+)/([^/]+)/versions/(.+)"
AZUREML_CLI_SYSTEM_EXECUTED_ENV_VAR = "AZUREML_CLI_SYSTEM_EXECUTED"
DOCSTRING_TEMPLATE = ".. note::    {0} {1}\n\n"
DOCSTRING_DEFAULT_INDENTATION = 8
EXPERIMENTAL_CLASS_MESSAGE = "This is an experimental class,"
EXPERIMENTAL_METHOD_MESSAGE = "This is an experimental method,"
EXPERIMENTAL_FIELD_MESSAGE = "This is an experimental field,"
EXPERIMENTAL_LINK_MESSAGE = (
    "and may change at any time. Please see https://aka.ms/azuremlexperimental for more information."
)
REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT = "\nVisit this link to refer to the {} schema if needed: {}."
STORAGE_AUTH_MISMATCH_ERROR = "AuthorizationPermissionMismatch"
SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME = "best_child_run_id"
BATCH_JOB_CHILD_RUN_OUTPUT_NAME = "score"
DEFAULT_ARTIFACT_STORE_OUTPUT_NAME = "default"
DEFAULT_EXPERIMENT_NAME = "Default"

CREATE_ENVIRONMENT_ERROR_MESSAGE = (
    "It looks like you are trying to specify a conda file for the --file/-f argument. "
    "--file/-f is reserved for the Azure ML Environment definition (see schema here: {}). "
    "To specify a conda file via command-line argument, please use --conda-file/-c argument."
)
API_URL_KEY = "api"
ANONYMOUS_ENV_NAME = "CliV2AnonymousEnvironment"
SKIP_VALIDATION_MESSAGE = "To skip this validation use the --skip-validation param"
MLTABLE_METADATA_SCHEMA_URL_FALLBACK = "https://azuremlschemasprod.azureedge.net/latest/MLTable.schema.json"
INVOCATION_ZIP_FILE = "invocation.zip"
INVOCATION_BAT_FILE = "Invocation.bat"
INVOCATION_BASH_FILE = "Invocation.sh"
AZUREML_RUN_SETUP_DIR = "azureml-setup"
AZUREML_RUNS_DIR = "azureml_runs"
EXECUTION_SERVICE_URL_KEY = "&fake="
LOCAL_JOB_FAILURE_MSG = "Failed to start local executable job.\n Detailed message: {}"
STORAGE_ACCOUNT_URLS = {
    "AzureBlob": "https://{}.blob.{}",
    "AzureDataLakeGen2": "https://{}.dfs.{}",
    "AzureFile": "https://{}.file.{}",
}

DEFAULT_LABEL_NAME = "default"
DEFAULT_COMPONENT_VERSION = "azureml_default"
ANONYMOUS_COMPONENT_NAME = "azureml_anonymous"
GIT_PATH_PREFIX = "git+"
SCHEMA_VALIDATION_ERROR_TEMPLATE = (
    "\n{text_color}{description}\n{error_msg}{reset}\n\n"
    "Details: {parsed_error_details}\n"
    "Resolutions: {resolutions}"
    "If using the CLI, you can also check the full log in debug mode for more details by adding --debug "
    "to the end of your command\n"
    "\nAdditional Resources: The easiest way to author a yaml specification file is using IntelliSense and "
    "auto-completion Azure ML VS code extension provides: "
    "{link_color}https://code.visualstudio.com/docs/datascience/azure-machine-learning.{reset} "
    "To set up VS Code, visit {link_color}https://docs.microsoft.com/azure/machine-learning/how-to-setup-vs-"
    "code{reset}\n"
)

YAML_CREATION_ERROR_DESCRIPTION = (
    "The yaml file you provided does not match the prescribed schema "
    "for {entity_type} yaml files and/or has the following issues:\n"
)
DATASTORE_SCHEMA_TYPES = [
    "AzureFileSchema",
    "AzureBlobSchema",
    "AzureDataLakeGen2Schema",
    "AzureStorageSchema",
    "AzureDataLakeGen1Schema",
]
LOCAL_PATH = "local_path"
SPARK_ENVIRONMENT_WARNING_MESSAGE = (
    "Spark job will only install the packages defined in the Conda configuration. It "
    "will not create a docker container using the image defined in the environment."
)


class AzureMLResourceType:
    """AzureMLResourceType is a class that defines the resource types that are supported by the SDK/CLI."""

    CODE = "codes"
    """Code resource type."""
    COMPUTE = "computes"
    """Compute resource type."""
    DATA = "data"
    """Data resource type."""
    DATASTORE = "datastores"
    """Datastore resource type."""
    ONLINE_ENDPOINT = "online_endpoints"
    """Online endpoint resource type."""
    BATCH_ENDPOINT = "batch_endpoints"
    """Batch endpoint resource type."""
    ONLINE_DEPLOYMENT = "online_deployments"
    """Online deployment resource type."""
    DEPLOYMENT = "deployments"
    """Deployment resource type."""
    BATCH_DEPLOYMENT = "batch_deployments"
    """Batch deployment resource type."""
    ENVIRONMENT = "environments"
    """Environment resource type."""
    JOB = "jobs"
    """Job resource type."""
    MODEL = "models"
    """Model resource type."""
    VIRTUALCLUSTER = "virtualclusters"
    """Virtual cluster resource type."""
    WORKSPACE = "workspaces"
    """Workspace resource type."""
    WORKSPACE_CONNECTION = "workspace_connections"
    """Workspace connection resource type."""
    COMPONENT = "components"
    """Component resource type."""
    SCHEDULE = "schedules"
    """Schedule resource type."""
    REGISTRY = "registries"
    """Registry resource type."""
    CONNECTIONS = "connections"
    """Connections resource type."""
    FEATURE_SET = "feature_sets"
    """Feature set resource type."""
    FEATURE_STORE_ENTITY = "feature_store_entities"
    """Feature store entity resource type."""
    FEATURE_STORE = "feature_store"
    """Feature store resource type."""

    NAMED_TYPES = {
        JOB,
        COMPUTE,
        WORKSPACE,
        ONLINE_ENDPOINT,
        ONLINE_DEPLOYMENT,
        DATASTORE,
        SCHEDULE,
    }
    VERSIONED_TYPES = {MODEL, DATA, CODE, ENVIRONMENT, COMPONENT, FEATURE_SET, FEATURE_STORE_ENTITY}


class ArmConstants:
    """ArmConstants is a class that defines the constants used by the SDK/CLI for ARM operations.

    ArmConstants are used to define the names of the parameters that are used in the ARM templates that are used by the
    SDK/CLI.
    """

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
    LOG_ANALYTICS = "LogAnalytics"
    WORKSPACE = "Workspace"

    AZURE_MGMT_RESOURCE_API_VERSION = "2020-06-01"
    AZURE_MGMT_STORAGE_API_VERSION = "2019-06-01"
    AZURE_MGMT_APPINSIGHT_API_VERSION = "2015-05-01"
    AZURE_MGMT_KEYVAULT_API_VERSION = "2019-09-01"
    AZURE_MGMT_CONTAINER_REG_API_VERSION = "2019-05-01"

    DEFAULT_URL = "https://management.azure.com/metadata/endpoints?api-version=2019-05-01"
    METADATA_URL_ENV_NAME = "ARM_CLOUD_METADATA_URL"
    REGISTRY_DISCOVERY_DEFAULT_REGION = "west"
    REGISTRY_DISCOVERY_REGION_ENV_NAME = "REGISTRY_DISCOVERY_ENDPOINT_REGION"
    REGISTRY_ENV_URL = "REGISTRY_DISCOVERY_ENDPOINT_URL"


class HttpResponseStatusCode:
    """Http response status code."""

    NOT_FOUND = 404
    """Not found."""


class OperationStatus:
    """Operation status class.

    Operation status is used to indicate the status of an operation. It can be one of the following values: Succeeded,
    Failed, Canceled, Running.
    """

    SUCCEEDED = "Succeeded"
    """Succeeded."""
    FAILED = "Failed"
    """Failed."""
    CANCELED = "Canceled"
    """Canceled."""
    RUNNING = "Running"
    """Running."""


class CommonYamlFields:
    """Common yaml fields.

    Common yaml fields are used to define the common fields in yaml files. It can be one of the following values: type,
    name, $schema.
    """

    TYPE = "type"
    """Type."""
    NAME = "name"
    """Name."""
    SCHEMA = "$schema"
    """Schema."""


class GitProperties:
    """GitProperties is a class that defines the constants used by the SDK/CLI for Git operations.

    Gitproperties are used to define the names of the properties that are used in the Git operations that are used by
    the SDK/CLI. These properties are used to set the Git properties in the run history.
    """

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


class LROConfigurations:
    """LRO configurations class.

    LRO configurations are used to define the configurations for long running operations. It can be one of the following
    values: MAX_WAIT_COUNT, POLLING_TIMEOUT, POLL_INTERVAL, SLEEP_TIME.
    """

    MAX_WAIT_COUNT = 400
    """Max wait count."""
    POLLING_TIMEOUT = 720
    """Polling timeout."""
    POLL_INTERVAL = 5
    """Poll interval."""
    SLEEP_TIME = 5
    """Sleep time."""


class OrderString:
    """Order string class.

    Order string is used to define the order string for list operations. It can be one of the following values:
    CREATED_AT, CREATED_AT_DESC.
    """

    CREATED_AT = "createdtime asc"
    """Created at."""
    CREATED_AT_DESC = "createdtime desc"
    """Created at desc."""


class YAMLRefDocLinks:
    """YAML reference document links.

    YAML reference document links are used to define the reference document links for yaml files.
    """

    WORKSPACE = "https://aka.ms/ml-cli-v2-workspace-yaml-reference"
    ENVIRONMENT = "https://aka.ms/ml-cli-v2-environment-yaml-reference"
    DATA = "https://aka.ms/ml-cli-v2-data-yaml-reference"
    MODEL = "https://aka.ms/ml-cli-v2-model-yaml-reference"
    AML_COMPUTE = "https://aka.ms/ml-cli-v2-compute-aml-yaml-reference"
    COMPUTE_INSTANCE = "https://aka.ms/ml-cli-v2-compute-instance-yaml-reference"
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
    JOB_SCHEDULE = "https://aka.ms/ml-cli-v2-schedule-yaml-reference"
    REGISTRY = "https://aka.ms/ml-cli-v2-registry-yaml-reference"
    FEATURE_STORE = "https://aka.ms/ml-cli-v2-featurestore-yaml-reference"
    FEATURE_SET = "https://aka.ms/ml-cli-v2-featureset-yaml-reference"
    FEATURE_STORE_ENTITY = "https://aka.ms/ml-cli-v2-featurestore-entity-yaml-reference"


class YAMLRefDocSchemaNames:
    """YAML reference document schema names.

    YAML reference document schema names are used to define the reference document schema names for yaml files.
    """

    WORKSPACE = "Workspace"
    """Workspace."""
    ENVIRONMENT = "Environment"
    """Environment."""
    DATA = "Data"
    """Data."""
    MODEL = "Model"
    """Model."""
    AML_COMPUTE = "AMLCompute"
    """AML compute."""
    COMPUTE_INSTANCE = "ComputeInstance"
    """Compute instance."""
    VIRTUAL_MACHINE_COMPUTE = "VirtualMachineCompute"
    """Virtual machine compute."""
    COMMAND_JOB = "CommandJob"
    """Command job."""
    SWEEP_JOB = "SweepJob"
    """Sweep job."""
    PARALLEL_JOB = "ParallelJob"
    """Parallel job."""
    PIPELINE_JOB = "PipelineJob"
    """Pipeline job."""
    DATASTORE_BLOB = "AzureBlobDatastore"
    """Azure blob datastore."""
    DATASTORE_FILE = "AzureFileDatastore"
    """Azure file datastore."""
    DATASTORE_DATA_LAKE_GEN_1 = "AzureDataLakeGen1Datastore"
    """Azure data lake gen 1 datastore."""
    DATASTORE_DATA_LAKE_GEN_2 = "AzureDataLakeGen2Datastore"
    """Azure data lake gen 2 datastore."""
    ONLINE_ENDPOINT = "OnlineEndpoint"
    """Online endpoint."""
    BATCH_ENDPOINT = "BatchEndpoint"
    """Batch endpoint."""
    MANAGED_ONLINE_DEPLOYMENT = "ManagedOnlineDeployment"
    """Managed online deployment."""
    KUBERNETES_ONLINE_DEPLOYMENT = "KubernetesOnlineDeployment"
    """Kubernetes online deployment."""
    BATCH_DEPLOYMENT = "BatchDeployment"
    """Batch deployment."""
    COMMAND_COMPONENT = "CommandComponent"
    """Command component."""
    PARALLEL_COMPONENT = "ParallelComponent"
    """Parallel component."""
    JOB_SCHEDULE = "JobSchedule"
    """Job Schedule."""


class DockerTypes:
    """Docker types accepted by the SDK/CLI.

    Docker types are used to define the docker types accepted by the SDK/CLI.
    """

    IMAGE = "Image"
    """Image."""
    BUILD = "Build"
    """Build."""


class DataType:
    """Data types that a job or compute instance schedule accepts.

    The supported data types are: simple and dataflow.
    """

    SIMPLE = "Simple"
    """Simple data type."""
    DATAFLOW = "Dataflow"
    """Dataflow data type."""


class LoggingLevel:
    """Logging levels that a job or compute instance schedule accepts.

    Logging levels are case-insensitive. For example, "WARNING" and "warning" are both valid. The  supported logging
    levels are: warning, info, and debug.
    """

    WARN = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class TimeZone(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Time zones that a job or compute instance schedule accepts."""

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
    VENEZUELA_STANDARD_TIME = "Venezuela Standard Time"
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
    LORD_HOWE_STANDARD_TIME = "Lord Howe Standard Time"
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


class AssetTypes:
    """AssetTypes is an enumeration of values for the asset types of a dataset.

    Asset types are used to identify the type of an asset. An asset can be a file, folder, mlflow model, triton model,
    mltable or custom model.
    """

    URI_FILE = "uri_file"
    """URI file asset type."""
    URI_FOLDER = "uri_folder"
    """URI folder asset type."""
    MLTABLE = "mltable"
    """MLTable asset type."""
    MLFLOW_MODEL = "mlflow_model"
    """MLFlow model asset type."""
    TRITON_MODEL = "triton_model"
    """Triton model asset type."""
    CUSTOM_MODEL = "custom_model"
    """Custom model asset type."""


class InputTypes:
    """InputTypes is an enumeration of values for the input types of a dataset.

    Input types are used to identify the type of an asset.
    """

    INTEGER = "integer"
    """Integer input type."""
    NUMBER = "number"
    """Number input type."""
    STRING = "string"
    """String input type."""
    BOOLEAN = "boolean"
    """Boolean input type."""


class WorkspaceResourceConstants:
    """WorkspaceResourceConstants is an enumeration of values for the encryption status of a workspace.

    :param object: Flag to indicate that if the encryption is enabled or not.
    :type object: str
    """

    ENCRYPTION_STATUS_ENABLED = "Enabled"
    """Encryption is enabled."""


class InputOutputModes:
    """InputOutputModes is an enumeration of values for the input/output modes of a dataset.

    Input/output modes are used to identify the type of an asset when it is created using the API.
    """

    MOUNT = "mount"
    """Mount asset type."""

    DOWNLOAD = "download"
    """Download asset type."""
    UPLOAD = "upload"
    """Upload asset type."""
    RO_MOUNT = "ro_mount"
    """Read-only mount asset type."""
    RW_MOUNT = "rw_mount"
    """Read-write mount asset type."""
    EVAL_MOUNT = "eval_mount"
    """Evaluation mount asset type."""
    EVAL_DOWNLOAD = "eval_download"
    """Evaluation download asset type."""
    DIRECT = "direct"
    """Direct asset type."""


class LegacyAssetTypes:
    """LegacyAssetTypes is an enumeration of values for the legacy asset types.

    Legacy asset types are used to identify the type of an asset when it is created using the legacy API.
    """

    PATH = "path"
    """Path asset type."""


class PublicNetworkAccess:
    """PublicNetworkAccess is an enumeration of values for the public network access setting for a workspace.

    Public network access can be 'Enabled' or 'Disabled'. When enabled, Azure Machine Learning will allow all network
    traffic to the workspace. When disabled, Azure Machine Learning will only allow traffic from the Azure Virtual
    Network that the workspace is in.
    """

    ENABLED = "Enabled"
    """Enable public network access."""
    DISABLED = "Disabled"
    """Disable public network access."""


class ModelType:
    """ModelType is an enumeration of values for the model types.

    Model types are used to identify the type of a model when it is created using the API. Model types can be
    'CustomModel', 'MLFlowModel' or 'TritonModel'.
    """

    CUSTOM = "CustomModel"
    """Custom model type."""
    MLFLOW = "MLFlowModel"
    """MLFlow model type."""
    TRITON = "TritonModel"
    """Triton model type."""


class RollingRate:
    """RollingRate is an enumeration of values for the rolling rate of a dataset.

    Rolling rate can be 'day', 'hour' or 'minute'.
    """

    DAY = "day"
    """Day rolling rate."""
    HOUR = "hour"
    """Hour rolling rate."""
    MINUTE = "minute"
    """Minute rolling rate."""


class Scope:
    """Scope is an enumeration of values for the scope of an asset.

    Scope can be 'subscription' or 'resource_group'.
    """

    SUBSCRIPTION = "subscription"
    """Subscription scope."""
    RESOURCE_GROUP = "resource_group"
    """Resource group scope."""


class IdentityType:
    """IdentityType is an enumeration of values for the identity type of a workspace.

    Identity type can be 'aml_token', 'user_identity' or 'managed_identity'.
    """

    AML_TOKEN = "aml_token"
    """AML Token identity type."""
    USER_IDENTITY = "user_identity"
    """User identity type."""
    MANAGED_IDENTITY = "managed_identity"
    """Managed identity type."""


class Boolean:
    """Boolean is an enumeration of values for the boolean type.

    Boolean type can be 'true' or 'false'.
    """

    TRUE = "true"
    """True boolean type."""
    FALSE = "false"
    """False boolean type."""


class InferenceServerType:
    AZUREML_ONLINE = "azureml_online"
    AZUREML_BATCH = "azureml_batch"
    TRITON = "triton"
    CUSTOM = "custom"


class IPProtectionLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ALL = "all"
    NONE = "none"


class AzureDevopsArtifactsType:
    ARTIFACT = "artifact"


class ScheduleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    JOB = "job"
    MONITOR = "monitor"
    DATA_IMPORT = "data_import"


class AutoDeleteCondition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CREATED_GREATER_THAN = "created_greater_than"
    LAST_ACCESSED_GREATER_THAN = "last_accessed_greater_than"
