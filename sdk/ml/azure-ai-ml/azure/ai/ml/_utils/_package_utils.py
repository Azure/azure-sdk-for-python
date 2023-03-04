# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging

from typing import Any, Callable, Optional, Union


from azure.ai.ml.entities._deployment.deployment import Deployment

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    PackageRequest,
    CodeConfiguration,
    BaseEnvironmentId,
    ModelConfiguration,
    AzureMLOnlineInferencingServer,
)
from azure.ai.ml._utils._asset_utils import _get_next_version_from_container
from azure.ai.ml._utils._logger_utils import initialize_logger_info

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="")


def package_deployment(deployment: Deployment, all_ops) -> Deployment:
    model_str = deployment.model
    model_version = model_str.split("/")[-1]
    model_name = model_str.split("/")[-3]
    model_ops = all_ops["models"]
    env_ops = all_ops["environments"]
    target_environment_name = "packaged-env"
    # might need later
    # target_environment_version = None
    # if not target_environment_version:
    #     target_environment_version = _get_next_version_from_container(
    #         name=target_environment_name,
    #         container_operation=env_ops._containers_operations,
    #         resource_group_name=env_ops._resource_group_name,
    #         workspace_name=env_ops._workspace_name,
    #     )

    package_request = PackageRequest(
        target_environment_name=target_environment_name,
        # target_environment_version=target_environment_version,
        base_environment_source=BaseEnvironmentId(
            base_environment_source_type="EnvironmentAsset", resource_id=deployment.environment
        ),
        inferencing_server=AzureMLOnlineInferencingServer(
            code_configuration=CodeConfiguration(
                code_id=deployment.code_configuration.code,
                scoring_script=deployment.code_configuration.scoring_script,
            )
        ),
        model_configuration=ModelConfiguration(mode="Download", mount_path="."),
    )
    try:
        package_request.base_environment_source.resource_id = "azureml:/" + deployment.environment
        package_request.inferencing_server.code_configuration.code_id = "azureml:/" + deployment.code_configuration.code
        packaged_env = model_ops.begin_package(model_name, model_version, package_request=package_request)
    except Exception as e:
        raise
    deployment.environment = packaged_env.target_environment_id
    deployment.model = None
    deployment.code_configuration = None
    return deployment
