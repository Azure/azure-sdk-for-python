# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import uuid
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from typing_extensions import Self

from azure.core import PipelineClient
from azure.core.credentials import TokenCredential
from azure.core.pipeline import policies

from ._client import AIProjectClient as ClientGenerated
from ._configuration import AIProjectClientConfiguration
from ._serialization import Deserializer, Serializer
from .operations import AgentsOperations, ConnectionsOperations, EvaluationsOperations, TelemetryOperations
from .operations._patch import InferenceOperations


class AIProjectClient(
    ClientGenerated
):  # pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes
    def __init__(  # pylint: disable=super-init-not-called,too-many-statements
        self,
        endpoint: str,
        subscription_id: str,
        resource_group_name: str,
        project_name: str,
        credential: "TokenCredential",
        **kwargs: Any,
    ) -> None:
        # TODO: Validate input formats with regex match (e.g. subscription ID)
        if not endpoint:
            raise ValueError("endpoint is required")
        if not subscription_id:
            raise ValueError("subscription_id ID is required")
        if not resource_group_name:
            raise ValueError("resource_group_name is required")
        if not project_name:
            raise ValueError("project_name is required")
        if not credential:
            raise ValueError("credential is required")
        if "api_version" in kwargs:
            raise ValueError("No support for overriding the API version")
        if "credential_scopes" in kwargs:
            raise ValueError("No support for overriding the credential scopes")

        kwargs0 = kwargs.copy()
        kwargs1 = kwargs.copy()
        kwargs2 = kwargs.copy()
        kwargs3 = kwargs.copy()

        # For getting AppInsights connection string from the AppInsights resource.
        # The AppInsights resource URL is not known at this point. We need to get it from the
        # AzureML "Workspace - Get" REST API call. It will have the form:
        # https://management.azure.com/subscriptions/{appinsights_subscription_id}/resourceGroups/{appinsights_resource_group_name}/providers/microsoft.insights/components/{appinsights_resource_name}
        _endpoint0 = "https://management.azure.com"
        self._config0: AIProjectClientConfiguration = AIProjectClientConfiguration(
            endpoint=endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            project_name=project_name,
            credential=credential,
            api_version="2020-02-02",
            credential_scopes=["https://management.azure.com/.default"],
            **kwargs0,
        )

        _policies0 = kwargs0.pop("policies", None)
        if _policies0 is None:
            _policies0 = [
                policies.RequestIdPolicy(**kwargs0),
                self._config0.headers_policy,
                self._config0.user_agent_policy,
                self._config0.proxy_policy,
                policies.ContentDecodePolicy(**kwargs0),
                self._config0.redirect_policy,
                self._config0.retry_policy,
                self._config0.authentication_policy,
                self._config0.custom_hook_policy,
                self._config0.logging_policy,
                policies.DistributedTracingPolicy(**kwargs0),
                policies.SensitiveHeaderCleanupPolicy(**kwargs0) if self._config0.redirect_policy else None,
                self._config0.http_logging_policy,
            ]
        self._client0: PipelineClient = PipelineClient(base_url=_endpoint0, policies=_policies0, **kwargs0)

        # For Endpoints operations (listing connections, getting connection properties, getting project properties)
        _endpoint1 = (
            "https://management.azure.com/"
            + f"subscriptions/{subscription_id}/"
            + f"resourceGroups/{resource_group_name}/"
            + "providers/Microsoft.MachineLearningServices/"
            + f"workspaces/{project_name}"
        )
        self._config1: AIProjectClientConfiguration = AIProjectClientConfiguration(
            endpoint=endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            project_name=project_name,
            credential=credential,
            api_version="2024-07-01-preview",
            credential_scopes=["https://management.azure.com/.default"],
            **kwargs1,
        )
        _policies1 = kwargs1.pop("policies", None)
        if _policies1 is None:
            _policies1 = [
                policies.RequestIdPolicy(**kwargs1),
                self._config1.headers_policy,
                self._config1.user_agent_policy,
                self._config1.proxy_policy,
                policies.ContentDecodePolicy(**kwargs1),
                self._config1.redirect_policy,
                self._config1.retry_policy,
                self._config1.authentication_policy,
                self._config1.custom_hook_policy,
                self._config1.logging_policy,
                policies.DistributedTracingPolicy(**kwargs1),
                policies.SensitiveHeaderCleanupPolicy(**kwargs1) if self._config1.redirect_policy else None,
                self._config1.http_logging_policy,
            ]
        self._client1: PipelineClient = PipelineClient(base_url=_endpoint1, policies=_policies1, **kwargs1)

        # For Agents operations
        _endpoint2 = f"{endpoint}/agents/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{project_name}"  # pylint: disable=line-too-long
        self._config2 = AIProjectClientConfiguration(
            endpoint=endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            project_name=project_name,
            credential=credential,
            api_version="2024-07-01-preview",  # TODO: Update me
            credential_scopes=["https://ml.azure.com/.default"],
            **kwargs2,
        )
        _policies2 = kwargs2.pop("policies", None)
        if _policies2 is None:
            _policies2 = [
                policies.RequestIdPolicy(**kwargs2),
                self._config2.headers_policy,
                self._config2.user_agent_policy,
                self._config2.proxy_policy,
                policies.ContentDecodePolicy(**kwargs2),
                self._config2.redirect_policy,
                self._config2.retry_policy,
                self._config2.authentication_policy,
                self._config2.custom_hook_policy,
                self._config2.logging_policy,
                policies.DistributedTracingPolicy(**kwargs2),
                policies.SensitiveHeaderCleanupPolicy(**kwargs2) if self._config2.redirect_policy else None,
                self._config2.http_logging_policy,
            ]
        self._client2: PipelineClient = PipelineClient(base_url=_endpoint2, policies=_policies2, **kwargs2)

        # For Cloud Evaluations operations
        # cSpell:disable-next-line
        _endpoint3 = f"{endpoint}/raisvc/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{project_name}"  # pylint: disable=line-too-long
        self._config3 = AIProjectClientConfiguration(
            endpoint=endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            project_name=project_name,
            credential=credential,
            api_version="2024-07-01-preview",  # TODO: Update me
            credential_scopes=["https://ml.azure.com/.default"],  # TODO: Update once service changes are ready
            **kwargs3,
        )
        _policies3 = kwargs3.pop("policies", None)
        if _policies3 is None:
            _policies3 = [
                policies.RequestIdPolicy(**kwargs3),
                self._config3.headers_policy,
                self._config3.user_agent_policy,
                self._config3.proxy_policy,
                policies.ContentDecodePolicy(**kwargs3),
                self._config3.redirect_policy,
                self._config3.retry_policy,
                self._config3.authentication_policy,
                self._config3.custom_hook_policy,
                self._config3.logging_policy,
                policies.DistributedTracingPolicy(**kwargs3),
                policies.SensitiveHeaderCleanupPolicy(**kwargs3) if self._config3.redirect_policy else None,
                self._config3.http_logging_policy,
            ]
        self._client3: PipelineClient = PipelineClient(base_url=_endpoint3, policies=_policies3, **kwargs3)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

        self.telemetry = TelemetryOperations(
            self._client0, self._config0, self._serialize, self._deserialize, outer_instance=self
        )
        self.connections = ConnectionsOperations(self._client1, self._config1, self._serialize, self._deserialize)
        self.agents = AgentsOperations(self._client2, self._config2, self._serialize, self._deserialize)
        self.evaluations = EvaluationsOperations(self._client3, self._config3, self._serialize, self._deserialize)
        self.inference = InferenceOperations(self)

    def close(self) -> None:
        self._client0.close()
        self._client1.close()
        self._client2.close()
        self._client3.close()

    def __enter__(self) -> Self:
        self._client0.__enter__()
        self._client1.__enter__()
        self._client2.__enter__()
        self._client3.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client0.__exit__(*exc_details)
        self._client1.__exit__(*exc_details)
        self._client2.__exit__(*exc_details)
        self._client3.__exit__(*exc_details)

    @classmethod
    def from_connection_string(cls, conn_str: str, credential: "TokenCredential", **kwargs) -> Self:
        """
        Create an AIProjectClient from a connection string.

        :param str conn_str: The connection string, copied from your AI Studio project.
        :param TokenCredential credential: Credential used to authenticate requests to the service.
        :return: An AIProjectClient instance.
        :rtype: AIProjectClient
        """
        if not conn_str:
            raise ValueError("Connection string is required")
        parts = conn_str.split(";")
        if len(parts) != 4:
            raise ValueError("Invalid connection string format")
        endpoint = "https://" + parts[0]
        subscription_id = parts[1]
        resource_group_name = parts[2]
        project_name = parts[3]
        return cls(endpoint, subscription_id, resource_group_name, project_name, credential, **kwargs)

    def upload_file(self, file_path: Union[Path, str, PathLike]) -> Tuple[str, str]:
        """Upload a file to the Azure AI Studio project.
           This method required *azure-ai-ml* to be installed.

        :param file_path: The path to the file to upload.
        :type file_path: Union[str, Path, PathLike]
        :return: The tuple, containing asset id and asset URI of uploaded file.
        :rtype: Tuple[str]
        """
        try:
            from azure.ai.ml import MLClient  # type: ignore
            from azure.ai.ml.constants import AssetTypes  # type: ignore
            from azure.ai.ml.entities import Data  # type: ignore
        except ImportError as e:
            raise ImportError(
                "azure-ai-ml must be installed to use this function. Please install it using `pip install azure-ai-ml`"
            ) from e

        data = Data(
            path=str(file_path),
            type=AssetTypes.URI_FILE,
            name=str(uuid.uuid4()),  # generating random name
            is_anonymous=True,
            version="1",
        )

        ml_client = MLClient(
            self._config3.credential,
            self._config3.subscription_id,
            self._config3.resource_group_name,
            self._config3.project_name,
        )

        data_asset = ml_client.data.create_or_update(data)

        return data_asset.id, data_asset.path

    @property
    def scope(self) -> Dict[str, str]:
        return {
            "subscription_id": self._config3.subscription_id,
            "resource_group_name": self._config3.resource_group_name,
            "project_name": self._config3.project_name,
        }


__all__: List[str] = [
    "AIProjectClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
