# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=try-except-raise

import logging


from azure.ai.ml.entities import BatchDeployment, OnlineDeployment, Deployment
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    PackageRequest,
    CodeConfiguration,
    BaseEnvironmentId,
    AzureMLOnlineInferencingServer,
    AzureMLBatchInferencingServer,
)
from azure.ai.ml.constants._common import REGISTRY_URI_FORMAT

from azure.ai.ml._utils._logger_utils import initialize_logger_info

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="")


def package_deployment(deployment: Deployment, model_ops) -> Deployment:
    model_str = deployment.model
    model_version = model_str.split("/")[-1]
    model_name = model_str.split("/")[-3]
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

    package_request: Any = None
    is_registry = model_str.startswith(REGISTRY_URI_FORMAT)

    # Mutate the (shared v2023_04) nested models in place, then assemble the request. For a registry package the
    # request envelope is a byte-identical JSON-direct dict (the legacy v2021_10 ``PackageRequest`` wire) so no
    # v2021_10 model is required.
    if deployment.environment:
        base_environment_source.resource_id = (
            deployment.environment if is_registry else "azureml:/" + deployment.environment
        )
    if deployment.code_configuration:
        inferencing_server.code_configuration.code_id = (
            deployment.code_configuration.code
            if deployment.code_configuration.code.startswith(REGISTRY_URI_FORMAT)
            else "azureml:/" + deployment.code_configuration.code
        )

    if is_registry:
        package_request = {}
        if base_environment_source is not None:
            package_request["baseEnvironmentSource"] = base_environment_source.serialize()
        if inferencing_server is not None:
            package_request["inferencingServer"] = inferencing_server.serialize()
        package_request["targetEnvironmentId"] = target_environment_name
    else:
        package_request = PackageRequest(
            target_environment_name=target_environment_name,
            base_environment_source=base_environment_source,
            inferencing_server=inferencing_server,
        )

    try:
        packaged_env = model_ops.package(
            model_name,
            model_version,
            package_request=package_request,
            skip_to_rest=True,
        )
        if not model_str.startswith(REGISTRY_URI_FORMAT):
            deployment.environment = packaged_env.id
        else:
            deployment.environment = (
                packaged_env.get("targetEnvironmentId")
                if isinstance(packaged_env, dict)
                else packaged_env.target_environment_id
            )
        deployment.model = None
        deployment.code_configuration = None
    except Exception:
        raise
    return deployment
