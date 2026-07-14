# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=try-except-raise

import logging
from typing import Any


from azure.ai.ml.entities import BatchDeployment, OnlineDeployment, Deployment
from azure.ai.ml.constants._common import REGISTRY_URI_FORMAT

from azure.ai.ml._utils._logger_utils import initialize_logger_info

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="")


def package_deployment(deployment: Deployment, model_ops) -> Deployment:
    model_str = deployment.model
    model_version = model_str.split("/")[-1]
    model_name = model_str.split("/")[-3]
    target_environment_name = "packaged-env"

    is_registry = model_str.startswith(REGISTRY_URI_FORMAT)

    # The model-package models are not on the shared arm_ml_service client, so build every part of the
    # request as a JSON-direct wire dict. These are byte-identical to the legacy v2023_04 msrest models
    # (``AzureML*InferencingServer`` / ``BaseEnvironmentId`` / ``PackageRequest``) they replace.
    inferencing_server: Any = None
    if isinstance(deployment, OnlineDeployment):
        inferencing_server = {"serverType": "AzureMLOnline"}
    elif isinstance(deployment, BatchDeployment):
        inferencing_server = {"serverType": "AzureMLBatch"}

    if deployment.code_configuration and inferencing_server is not None:
        code_id = (
            deployment.code_configuration.code
            if deployment.code_configuration.code.startswith(REGISTRY_URI_FORMAT)
            else "azureml:/" + deployment.code_configuration.code
        )
        code_wire: Any = {"codeId": code_id}
        if deployment.code_configuration.scoring_script is not None:
            code_wire["scoringScript"] = deployment.code_configuration.scoring_script
        inferencing_server["codeConfiguration"] = code_wire

    base_environment_source: Any = None
    if deployment.environment:
        base_environment_source = {
            "baseEnvironmentSourceType": "EnvironmentAsset",
            "resourceId": (deployment.environment if is_registry else "azureml:/" + deployment.environment),
        }

    package_request: Any = None
    if is_registry:
        package_request = {}
        if base_environment_source is not None:
            package_request["baseEnvironmentSource"] = base_environment_source
        if inferencing_server is not None:
            package_request["inferencingServer"] = inferencing_server
        package_request["targetEnvironmentId"] = target_environment_name
    else:
        package_request = {"targetEnvironmentName": target_environment_name}
        if base_environment_source is not None:
            package_request["baseEnvironmentSource"] = base_environment_source
        if inferencing_server is not None:
            package_request["inferencingServer"] = inferencing_server

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
