# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class DeploymentType(object):
    K8S = "Kubernetes"
    MANAGED = "Managed"


class BatchDeploymentOutputAction:
    APPEND_ROW = "append_row"
    SUMMARY_ONLY = "summary_only"


class BatchDeploymentType:
    MODEL = "model"
    PIPELINE = "pipeline"


class EndpointDeploymentLogContainerType(object):
    STORAGE_INITIALIZER_REST = "StorageInitializer"
    INFERENCE_SERVER_REST = "InferenceServer"
    INFERENCE_SERVER = "inference-server"
    STORAGE_INITIALIZER = "storage-initializer"


SmallSKUs = ["standard_ds1_v2", "standard_ds2_v2"]
DEFAULT_MDC_PATH = "azureml://datastores/workspaceblobstore/paths/modelDataCollector"
