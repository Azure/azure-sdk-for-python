# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping # pylint:disable=import-error
from typing import IO, Any, Callable, Dict, Optional, TypeVar, Union, cast, overload

from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from .._utils.model_base import _deserialize
from ..models import (
    CreateDeploymentDetails,
    DeleteDeploymentDetails,
    DeploymentDeleteFromResourcesState,
    DeploymentState,
    ProjectDeployment,
)
from ._operations import DeploymentOperations as DeploymentOperationsGenerated

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]

class DeploymentOperations(DeploymentOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_delete_deployment(self, deployment_name: str, **kwargs: Any) -> LROPoller[None]:  # type: ignore[override]
        """Deletes a project deployment.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_delete_deployment(
            project_name=self._project_name, deployment_name=deployment_name, **kwargs
        )

    @overload
    def begin_delete_deployment_from_resources(
        self,
        deployment_name: str,
        body: DeleteDeploymentDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.DeleteDeploymentDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: Union[DeleteDeploymentDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.DeleteDeploymentDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_delete_deployment_from_resources(
            project_name=self._project_name,
            deployment_name=deployment_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @overload
    def begin_deploy_project(
        self,
        deployment_name: str,
        body: CreateDeploymentDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CreateDeploymentDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_deploy_project(
        self, deployment_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_deploy_project(
        self, deployment_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_deploy_project(
        self, deployment_name: str, body: Union[CreateDeploymentDetails, JSON, IO[bytes]],*, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CreateDeploymentDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_deploy_project(
            project_name=self._project_name,
            deployment_name=deployment_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    def get_deployment(self, deployment_name: str, **kwargs: Any) -> ProjectDeployment:  # type: ignore[override]
        return super().get_deployment(project_name=self._project_name, deployment_name=deployment_name, **kwargs)

    @distributed_trace
    def _get_deployment_delete_from_resources_status(  # type: ignore[override]
        self, deployment_name: str, job_id: str, **kwargs: Any
    ) -> DeploymentDeleteFromResourcesState:
        return super()._get_deployment_delete_from_resources_status(
            project_name=self._project_name, deployment_name=deployment_name, job_id=job_id, **kwargs
        )

    @distributed_trace
    def _get_deployment_status(  # type: ignore[override]
        self, deployment_name: str, job_id: str, **kwargs: Any
    ) -> DeploymentState:
        return super()._get_deployment_status(
            project_name=self._project_name, deployment_name=deployment_name, job_id=job_id, **kwargs
        )
