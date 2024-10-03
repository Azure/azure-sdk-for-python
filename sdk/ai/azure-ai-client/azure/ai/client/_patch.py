# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
import logging
import base64
import json
from typing import List, Tuple, Union, Any
from azure.core.credentials import TokenCredential, AccessToken
from azure.core import PipelineClient
from azure.core.pipeline import policies
from ._configuration import ClientConfiguration
from ._serialization import Deserializer, Serializer
from .operations import AgentsOperations, EndpointsOperations, EvaluationsOperations
from ._client import Client as ClientGenerated

logger = logging.getLogger(__name__)


class AzureAIClient(ClientGenerated):

    def __init__(
        self,
        endpoint: str,
        subscription_id: str,
        resource_group_name: str,
        workspace_name: str,
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
        if not workspace_name:
            raise ValueError("workspace_name is required")
        if not credential:
            raise ValueError("Credential is required")
        if "api_version" in kwargs:
            raise ValueError("No support for overriding the API version")
        if "credential_scopes" in kwargs:
            raise ValueError("No support for overriding the credential scopes")

        kwargs1 = kwargs.copy()
        kwargs2 = kwargs.copy()
        kwargs3 = kwargs.copy()

        # For Endpoints operations (enumerating connections, getting SAS tokens)
        _endpoint1 = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"  # pylint: disable=line-too-long
        self._config1 = ClientConfiguration(
            endpoint=endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            credential=credential,
            api_version="2024-07-01-preview",
            credential_scopes=["https://management.azure.com"],
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
        _endpoint2 = f"{endpoint}/assistants/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"  # pylint: disable=line-too-long
        self._config2 = ClientConfiguration(
            endpoint=endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            credential=credential,
            api_version="2024-07-01-preview",  # TODO: Update me
            credential_scopes=["https://ml.azure.com"],
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
        _endpoint3 = f"{endpoint}/raisvc/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"  # pylint: disable=line-too-long
        self._config3 = ClientConfiguration(
            endpoint=endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            credential=credential,
            api_version="2024-07-01-preview",  # TODO: Update me
            credential_scopes=["https://ml.azure.com"],
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

        self.endpoints = EndpointsOperations(self._client1, self._config1, self._serialize, self._deserialize)
        self.agents = AgentsOperations(self._client2, self._config2, self._serialize, self._deserialize)
        self.evaluations = EvaluationsOperations(self._client3, self._config3, self._serialize, self._deserialize)

    @classmethod
    def from_connection_string(cls, connection: str, credential: "TokenCredential", **kwargs) -> "AzureAIClient":
        """
        Create an AzureAIClient from a connection string.

        :param connection: The connection string, copied from your AI Studio project.
        """
        if not connection:
            raise ValueError("Connection string is required")
        parts = connection.split(";")
        if len(parts) != 4:
            raise ValueError("Invalid connection string format")
        endpoint = parts[0]
        subscription_id = parts[1]
        resource_group_name = parts[2]
        workspace_name = parts[3]
        return cls(endpoint, subscription_id, resource_group_name, workspace_name, credential, **kwargs)


class SASTokenCredential(TokenCredential):
    def __init__(
        self,
        *,
        sas_token: str,
        credential: TokenCredential,
        subscription_id: str,
        resource_group_name: str,
        workspace_name: str,
        connection_name: str,
    ):
        self._sas_token = sas_token
        self._credential = credential
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name
        self._connection_name = connection_name
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self._sas_token)
        logger.debug("[SASTokenCredential.__init__] Exit. Given token expires on %s.", self._expires_on)

    @classmethod
    def _get_expiration_date_from_token(cls, jwt_token: str) -> datetime:
        payload = jwt_token.split(".")[1]
        padded_payload = payload + "=" * (4 - len(payload) % 4)  # Add padding if necessary
        decoded_bytes = base64.urlsafe_b64decode(padded_payload)
        decoded_str = decoded_bytes.decode("utf-8")
        decoded_payload = json.loads(decoded_str)
        expiration_date = decoded_payload.get("exp")
        return datetime.datetime.fromtimestamp(expiration_date, datetime.timezone.utc)

    def _refresh_token(self) -> None:
        logger.debug("[SASTokenCredential._refresh_token] Enter")
        ai_client = ClientGenerated(
            credential=self._credential,
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
        )

        connection = ai_client.connections.get(connection_name=self._connection_name, populate_secrets=True)

        self._sas_token = connection.properties.credentials.sas
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self._sas_token)
        logger.debug("[SASTokenCredential._refresh_token] Exit. New token expires on %s.", self._expires_on)

    def get_token(self) -> AccessToken:
        logger.debug("SASTokenCredential.get_token] Enter")
        if self._expires_on < datetime.datetime.now(datetime.timezone.utc):
            self._refresh_token()
        return AccessToken(self._sas_token, self._expires_on.timestamp())


__all__: List[str] = [
    "AzureAIClient",
    "SASTokenCredential",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
