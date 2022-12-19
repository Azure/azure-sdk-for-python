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
LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/{}/{}"
VERSIONED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}/{}/{}/versions/{}"
LABELLED_RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/{}/workspaces/{}/{}/{}/labels/{}"
DATASTORE_RESOURCE_ID = (
    "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/datastores/{}"
)
PROVIDER_RESOURCE_ID_WITH_VERSION = (
    "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/{}/{}/versions/{}"
)
ASSET_ID_FORMAT = "azureml://locations/{}/workspaces/{}/{}/{}/versions/{}"
VERSIONED_RESOURCE_NAME = "{}:{}"
LABELLED_RESOURCE_NAME = "{}@{}"
PYTHON = "python"
AML_TOKEN_YAML = "aml_token"
AAD_TOKEN_YAML = "aad_token"
KEY = "key"
DEFAULT_ARM_RETRY_INTERVAL = 60
COMPONENT_TYPE = "type"
TID_FMT = "&tid={}"
AZUREML_PRIVATE_FEATURES_ENV_VAR = "AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED"
AZUREML_INTERNAL_COMPONENTS_ENV_VAR = "AZURE_ML_INTERNAL_COMPONENTS_ENABLED"
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
REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT = "Visit this link to refer to the {} schema if needed: {}."
STORAGE_AUTH_MISMATCH_ERROR = "AuthorizationPermissionMismatch"
SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME = "best_child_run_id"
BATCH_JOB_CHILD_RUN_NAME = "batchscoring"
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
    "\n\nError: {description}\n{error_msg}\n\n"
    "Details: {parsed_error_details}\n"
    "Resolutions:\n{resolutions}"
    "If using the CLI, you can also check the full log in debug mode for more details by adding --debug "
    "to the end of your command\n"
    "Additional Resources: The easiest way to author a yaml specification file is using IntelliSense and "
    "auto-completion Azure ML VS code extension provides: "
    "https://code.visualstudio.com/docs/datascience/azure-machine-learning. "
    "To set up VS Code, visit https://docs.microsoft.com/azure/machine-learning/how-to-setup-vs-code\n"
)

YAML_CREATION_ERROR_DESCRIPTION = (
    "The yaml file you provided does not match the prescribed schema "
    "for {entity_type} yaml files and/or has the following issues:"
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


class AzureMLResourceType(object):
    CODE = "codes"
    COMPUTE = "computes"
    DATA = "data"
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
    SCHEDULE = "schedules"
    REGISTRY = "registries"

    NAMED_TYPES = {
        JOB,
        COMPUTE,
        WORKSPACE,
        ONLINE_ENDPOINT,
        ONLINE_DEPLOYMENT,
        DATASTORE,
        SCHEDULE,
    }
    VERSIONED_TYPES = {MODEL, DATA, CODE, ENVIRONMENT, COMPONENT}


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


class HttpResponseStatusCode(object):
    NOT_FOUND = 404


class OperationStatus(object):
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELED = "Canceled"
    RUNNING = "Running"


class CommonYamlFields(object):
    TYPE = "type"
    NAME = "name"
    SCHEMA = "$schema"


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


class LROConfigurations:
    MAX_WAIT_COUNT = 400
    POLLING_TIMEOUT = 720
    POLL_INTERVAL = 5
    SLEEP_TIME = 5


class OrderString:
    CREATED_AT = "createdtime asc"
    CREATED_AT_DESC = "createdtime desc"


class YAMLRefDocLinks:
    WORKSPACE = "https://aka.ms/ml-cli-v2-workspace-yaml-reference"
    ENVIRONMENT = "https://aka.ms/ml-cli-v2-environment-yaml-reference"
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
    SCHEDULE = "https://aka.ms/ml-cli-v2-schedule-yaml-reference"
    REGISTRY = "https://aka.ms/ml-cli-v2-registry-yaml-reference"


class YAMLRefDocSchemaNames:
    WORKSPACE = "Workspace"
    ENVIRONMENT = "Environment"
    DATA = "Data"
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
    SCHEDULE = "Schedule"


class DockerTypes:
    IMAGE = "Image"
    BUILD = "Build"


class DataType:
    SIMPLE = "Simple"
    DATAFLOW = "Dataflow"


class LoggingLevel:
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
    URI_FILE = "uri_file"
    URI_FOLDER = "uri_folder"
    MLTABLE = "mltable"
    MLFLOW_MODEL = "mlflow_model"
    TRITON_MODEL = "triton_model"
    CUSTOM_MODEL = "custom_model"


class WorkspaceResourceConstants(object):
    ENCRYPTION_STATUS_ENABLED = "Enabled"


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


class PublicNetworkAccess:
    ENABLED = "Enabled"
    DISABLED = "Disabled"


class ModelType:
    CUSTOM = "CustomModel"
    MLFLOW = "MLFlowModel"
    TRITON = "TritonModel"


class RollingRate:
    YEAR = "year"
    MONTH = "month"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"


class Scope:
    SUBSCRIPTION="subscription"
    RESOURCE_GROUP="resource_group"


class IdentityType:
    AML_TOKEN = "aml_token"
    USER_IDENTITY = "user_identity"
    MANAGED_IDENTITY = "managed_identity"
