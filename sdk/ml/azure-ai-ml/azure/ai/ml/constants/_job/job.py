# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class DistributionType:
    MPI = "mpi"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    RAY = "ray"


class JobType(object):
    COMMAND = "command"
    SWEEP = "sweep"
    PIPELINE = "pipeline"
    AUTOML = "automl"
    COMPONENT = "component"
    BASE = "base"
    PARALLEL = "parallel"
    IMPORT = "import"
    SPARK = "spark"
    DATA_TRANSFER = "data_transfer"


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


class ImportSourceType:
    AZURESQLDB = "azuresqldb"
    AZURESYNAPSEANALYTICS = "azuresynapseanalytics"
    SNOWFLAKE = "snowflake"
    S3 = "s3"


class JobComputePropertyFields(object):
    # Legacy name
    AISUPERCOMPUTER = "AISuperComputer"
    SINGULARITY = "Singularity"
    ITP = "itp"
    TARGET_SELECTOR = "target_selector"


class SparkConfKey:
    DRIVER_CORES = "driver_cores"
    DRIVER_MEMORY = "driver_memory"
    EXECUTOR_CORES = "executor_cores"
    EXECUTOR_MEMORY = "executor_memory"
    EXECUTOR_INSTANCES = "executor_instances"
    DYNAMIC_ALLOCATION_MIN_EXECUTORS = "dynamic_allocation_min_executors"
    DYNAMIC_ALLOCATION_MAX_EXECUTORS = "dynamic_allocation_max_executors"
    DYNAMIC_ALLOCATION_ENABLED = "dynamic_allocation_enabled"


class RestSparkConfKey:
    DRIVER_CORES = "spark.driver.cores"
    DRIVER_MEMORY = "spark.driver.memory"
    EXECUTOR_CORES = "spark.executor.cores"
    EXECUTOR_MEMORY = "spark.executor.memory"
    EXECUTOR_INSTANCES = "spark.executor.instances"
    DYNAMIC_ALLOCATION_MIN_EXECUTORS = "spark.dynamicAllocation.minExecutors"
    DYNAMIC_ALLOCATION_MAX_EXECUTORS = "spark.dynamicAllocation.maxExecutors"
    DYNAMIC_ALLOCATION_ENABLED = "spark.dynamicAllocation.enabled"


class JobServiceTypeNames:
    class EntityNames:
        CUSTOM = "custom"
        TRACKING = "Tracking"
        STUDIO = "Studio"
        JUPYTER_LAB = "jupyter_lab"
        SSH = "ssh"
        TENSOR_BOARD = "tensor_board"
        VS_CODE = "vs_code"
        RAY_DASHBOARD = "RayDashboard"

    class RestNames:
        CUSTOM = "Custom"
        TRACKING = "Tracking"
        STUDIO = "Studio"
        JUPYTER_LAB = "JupyterLab"
        SSH = "SSH"
        TENSOR_BOARD = "TensorBoard"
        VS_CODE = "VSCode"
        RAY_DASHBOARD = "RayDashboard"

    ENTITY_TO_REST = {
        EntityNames.CUSTOM: RestNames.CUSTOM,
        EntityNames.TRACKING: RestNames.TRACKING,
        EntityNames.STUDIO: RestNames.STUDIO,
        EntityNames.JUPYTER_LAB: RestNames.JUPYTER_LAB,
        EntityNames.SSH: RestNames.SSH,
        EntityNames.TENSOR_BOARD: RestNames.TENSOR_BOARD,
        EntityNames.VS_CODE: RestNames.VS_CODE,
        EntityNames.RAY_DASHBOARD: RestNames.RAY_DASHBOARD,
    }

    REST_TO_ENTITY = {v: k for k, v in ENTITY_TO_REST.items()}

    NAMES_ALLOWED_FOR_PUBLIC = [EntityNames.JUPYTER_LAB, EntityNames.SSH, EntityNames.TENSOR_BOARD, EntityNames.VS_CODE]


class JobTierNames:
    class EntityNames:
        Spot = "spot"
        Basic = "basic"
        Standard = "standard"
        Premium = "premium"

    class RestNames:
        Spot = "Spot"
        Basic = "Basic"
        Standard = "Standard"
        Premium = "Premium"

    ENTITY_TO_REST = {
        EntityNames.Spot: RestNames.Spot,
        EntityNames.Basic: RestNames.Basic,
        EntityNames.Standard: RestNames.Standard,
        EntityNames.Premium: RestNames.Premium,
    }

    REST_TO_ENTITY = {v: k for k, v in ENTITY_TO_REST.items()}

    ALLOWED_NAMES = [EntityNames.Spot, EntityNames.Basic, EntityNames.Standard, EntityNames.Premium]


class JobPriorityValues:
    class EntityValues:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    class RestValues:
        LOW = 1
        MEDIUM = 2
        HIGH = 3

    ENTITY_TO_REST = {
        EntityValues.LOW: RestValues.LOW,
        EntityValues.MEDIUM: RestValues.MEDIUM,
        EntityValues.HIGH: RestValues.HIGH,
    }

    REST_TO_ENTITY = {v: k for k, v in ENTITY_TO_REST.items()}

    ALLOWED_VALUES = [EntityValues.LOW, EntityValues.MEDIUM, EntityValues.HIGH]
