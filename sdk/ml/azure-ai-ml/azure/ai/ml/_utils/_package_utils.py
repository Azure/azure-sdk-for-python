# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,try-except-raise

import logging


from azure.ai.ml.entities import BatchDeployment, OnlineDeployment, Deployment
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    PackageRequest,
    CodeConfiguration,
    BaseEnvironmentId,
    AzureMLOnlineInferencingServer,
    AzureMLBatchInferencingServer,
)
from azure.ai.ml._utils._logger_utils import initialize_logger_info

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="")


def package_deployment(deployment: Deployment, all_ops) -> Deployment:
    model_str = deployment.model
    model_version = model_str.split("/")[-1]
    model_name = model_str.split("/")[-3]
    model_ops = all_ops["models"]
    target_environment_name = "packaged-env"

    if deployment.code_configuration:
        code_configuration = CodeConfiguration(
            code_id=deployment.code_configuration.code,
            scoring_script=deployment.code_configuration.scoring_script,
        )
    else:
        code_configuration = None

    if isinstance(deployment, OnlineDeployment):
        inferencing_server = AzureMLOnlineInferencingServer(code_configuration=code_configuration)
    elif isinstance(deployment, BatchDeployment):
        inferencing_server = AzureMLBatchInferencingServer(code_configuration=code_configuration)
    else:
        inferencing_server = None

    if deployment.environment:
        base_environment_source = BaseEnvironmentId(
            base_environment_source_type="EnvironmentAsset", resource_id=deployment.environment
        )
    else:
        base_environment_source = None

    package_request = PackageRequest(
        target_environment_name=target_environment_name,
        base_environment_source=base_environment_source,
        inferencing_server=inferencing_server,
    )
    if deployment.environment:
        package_request.base_environment_source.resource_id = "azureml:/" + deployment.environment
    if deployment.code_configuration:
        package_request.inferencing_server.code_configuration.code_id = "azureml:/" + deployment.code_configuration.code
    try:
        packaged_env = model_ops.begin_package(
            model_name, model_version, package_request=package_request, skip_to_rest=True
        )
        deployment.environment = packaged_env.id
        deployment.model = None
        deployment.code_configuration = None
    except Exception:
        raise
    return deployment
