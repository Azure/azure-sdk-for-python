# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Any, Iterable, Optional

from azure.ai.ml._restclient.arm_ml_service import MachineLearningServicesMgmtClient as ServiceClient042024PreviewArm
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml.entities._autogen_entities.models import AzureOpenAIDeployment
from azure.core.paging import ItemPaged
from azure.core.rest import HttpRequest

from ._workspace_connections_operations import WorkspaceConnectionsOperations

module_logger = logging.getLogger(__name__)


class AzureOpenAIDeploymentOperations(_ScopeDependentOperations):
    """AzureOpenAIDeploymentOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient042024PreviewArm,
        connections_operations: WorkspaceConnectionsOperations,
    ):
        super().__init__(operation_scope, operation_config)
        self._service_client = service_client
        self._workspace_connections_operations = connections_operations

    # pylint: disable-next=unused-argument
    def list(self, connection_name: str, **kwargs: Any) -> Iterable[AzureOpenAIDeployment]:
        """List Azure OpenAI deployments of the workspace.

        :param connection_name: Name of the connection from which to list deployments
        :type connection_name: str
        :return: A list of Azure OpenAI deployments
        :rtype: ~typing.Iterable[~azure.ai.ml.entities.AzureOpenAIDeployment]
        """
        connection = self._workspace_connections_operations.get(connection_name)

        def _from_rest_add_connection_name(obj: Any) -> AzureOpenAIDeployment:
            from_rest_deployment = AzureOpenAIDeployment._from_rest_object(obj)  # type: ignore[attr-defined]
            from_rest_deployment.connection_name = connection_name
            from_rest_deployment.target_url = connection.target
            return from_rest_deployment

        # ``arm_ml_service`` has no ``connection.list_deployments`` operation, so call the ARM
        # ``.../connections/{name}/deployments`` list endpoint directly via ``send_request`` and page over
        # the arm-paginated result. On-the-wire request/response is unchanged (api-version 2024-04-01-preview).
        base_url = (
            f"/subscriptions/{self._subscription_id}"
            f"/resourceGroups/{self._resource_group_name}"
            f"/providers/Microsoft.MachineLearningServices/workspaces/{self._workspace_name}"
            f"/connections/{connection_name}/deployments"
        )

        def get_next(continuation_token: Optional[str] = None) -> Any:
            if continuation_token:
                request = HttpRequest("GET", continuation_token)
            else:
                request = HttpRequest("GET", base_url, params={"api-version": "2024-04-01-preview"})
            response = self._service_client.send_request(request)
            response.raise_for_status()
            return response

        def extract_data(response: Any) -> Any:
            body = response.json()
            elements = [_from_rest_add_connection_name(obj) for obj in (body.get("value") or [])]
            return body.get("nextLink") or None, iter(elements)

        return ItemPaged(get_next, extract_data)
