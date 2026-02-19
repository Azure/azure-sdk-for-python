# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Optional, Union

from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator import distributed_trace

from ._operations import DeploymentOperations as _GeneratedDeploymentOperations, JSON
from ...models import CreateDeploymentDetails


class DeploymentOperations(_GeneratedDeploymentOperations):
    """Deployment operations that handle both:
    - 2025-11-15-preview: azureResourceIds = List[AssignedProjectResource]
    - 2025-11-01:        azureResourceIds = List[str]
    """

    @distributed_trace
    async def begin_deploy_project(  # type: ignore[override]
        self,
        deployment_name: str,
        body: Union[CreateDeploymentDetails, JSON, Any],
        **kwargs: Any,
    ) -> AsyncLROPoller[None]:
        api_version: Optional[str] = getattr(self._config, "api_version", None)

        if not isinstance(body, CreateDeploymentDetails):
            return await super().begin_deploy_project(
                deployment_name=deployment_name,
                body=body,
                **kwargs,
            )

        # If no api_version or preview → use preview shape
        if api_version in (None, "2025-11-15-preview"):
            # For preview, we require assigned resources, because region is needed.
            if body.azure_resource_ids is None:
                # user tried to use GA-style strings but preview needs region
                if getattr(body, "_azure_resource_ids_strings", None):
                    raise ValueError(
                        "For api_version '2025-11-15-preview', azure_resource_ids must "
                        "be a list of AssignedProjectResource (with region), not plain strings."
                    )
            # Just send the model as-is
            return await super().begin_deploy_project(
                deployment_name=deployment_name,
                body=body,
                **kwargs,
            )

        # GA 2025-11-01 → azureResourceIds is List[str]
        if api_version == "2025-11-01":
            trained_model_label = body.trained_model_label

            # Prefer GA-style strings if user gave them
            str_ids = getattr(body, "_azure_resource_ids_strings", None)
            if str_ids is not None:
                azure_ids = str_ids
            else:
                # Otherwise derive from AssignedProjectResource list
                azure_ids = None
                if body.azure_resource_ids is not None:
                    azure_ids = [r.resource_id for r in body.azure_resource_ids]

            json_body: JSON = {"trainedModelLabel": trained_model_label}
            if azure_ids is not None:
                json_body["azureResourceIds"] = azure_ids

            return await super().begin_deploy_project(
                deployment_name=deployment_name,
                body=json_body,  # GA wire
                **kwargs,
            )

        # Any other version: fall back to default behavior
        return await super().begin_deploy_project(
            deployment_name=deployment_name,
            body=body,
            **kwargs,
        )
