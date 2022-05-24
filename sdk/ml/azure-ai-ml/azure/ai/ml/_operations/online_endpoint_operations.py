# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import time
from typing import Dict, Iterable, Union, Any

from azure.core.exceptions import HttpResponseError
from azure.core.polling import LROPoller
from azure.identity import ChainedTokenCredential

from azure.ai.ml._restclient.v2022_02_01_preview import (
    AzureMachineLearningWorkspaces as ServiceClient022022Preview,
)

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    EndpointAuthKeys,
    EndpointAuthToken,
    OnlineEndpointTrackedResourceArmPaginatedResult,
    RegenerateEndpointKeysRequest,
    KeyType,
)
from .operation_orchestrator import OperationOrchestrator

from azure.ai.ml.entities._assets import Data
from azure.ai.ml._utils._endpoint_utils import polling_wait, post_and_validate_response
from azure.ai.ml._utils.utils import (
    _get_mfe_base_url_from_discovery_service,
    modified_operation_client,
)
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations
from azure.ai.ml._operations._local_endpoint_helper import _LocalEndpointHelper
from azure.ai.ml.constants import (
    KEY,
    AzureMLResourceType,
    EndpointInvokeFields,
    LROConfigurations,
    EndpointKeyType,
)
from azure.ai.ml.entities import OnlineEndpoint, OnlineDeployment
from azure.ai.ml._utils._azureml_polling import AzureMLPolling

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


def _strip_zeroes_from_traffic(traffic: Dict[str, str]) -> Dict[str, str]:
    return {k: v for k, v in traffic.items() if v and int(v) != 0}


class OnlineEndpointOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client_02_2022_preview: ServiceClient022022Preview,
        all_operations: OperationsContainer,
        local_endpoint_helper: _LocalEndpointHelper,
        credentials: ChainedTokenCredential = None,
        **kwargs: Dict,
    ):
        super(OnlineEndpointOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._online_operation = service_client_02_2022_preview.online_endpoints
        self._online_deployment_operation = service_client_02_2022_preview.online_deployments
        self._all_operations = all_operations
        self._local_endpoint_helper = local_endpoint_helper
        self._credentials = credentials
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "OnlineEndpoint.List", ActivityType.PUBLICAPI)
    def list(self, local: bool = False) -> Iterable[OnlineEndpointTrackedResourceArmPaginatedResult]:
        """List endpoints of the workspace.

        :param (bool, optional) local: a flag to indicate whether to interact with endpoints in local Docker environment. Default: False.
        :return: a list of endpoints
        """
        if local:
            return self._local_endpoint_helper.list()
        return self._online_operation.list(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [OnlineEndpoint._from_rest_object(obj) for obj in objs],
            **self._init_kwargs,
        )

    @monitor_with_activity(logger, "OnlineEndpoint.ListKeys", ActivityType.PUBLICAPI)
    def list_keys(self, name: str) -> Union[EndpointAuthKeys, EndpointAuthToken]:
        """List the keys

        :param name str: the endpoint name
        :raise: Exception if cannot get online credentials
        :return Union[EndpointAuthKeys, EndpointAuthToken]: depending on the auth mode in the endpoint, returns either keys or token
        """
        return self._get_online_credentials(name=name)

    @monitor_with_activity(logger, "OnlineEndpoint.Get", ActivityType.PUBLICAPI)
    def get(
        self,
        name: str,
        local: bool = False,
    ) -> OnlineEndpoint:
        """Get a Endpoint resource.

        :param str name: Name of the endpoint.
        :param (bool, optional) local: a flag to indicate whether to interact with endpoints in local Docker environment. Default: False.
        :return: Endpoint object retrieved from the service.
        :rtype: OnlineEndpoint:
        """
        # first get the endpoint
        if local:
            return self._local_endpoint_helper.get(endpoint_name=name)

        endpoint = self._online_operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            **self._init_kwargs,
        )

        deployments_list = self._online_deployment_operation.list(
            endpoint_name=name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [OnlineDeployment._from_rest_object(obj) for obj in objs],
            **self._init_kwargs,
        )

        # populate deployments without traffic with zeroes in traffic map
        converted_endpoint = OnlineEndpoint._from_rest_object(endpoint)
        if deployments_list:
            for deployment in deployments_list:
                if not converted_endpoint.traffic.get(deployment.name) and not converted_endpoint.mirror_traffic.get(
                    deployment.name
                ):
                    converted_endpoint.traffic[deployment.name] = 0

        return converted_endpoint

    @monitor_with_activity(logger, "OnlineEndpoint.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str = None, local: bool = False, **kwargs: Any) -> LROPoller:
        """Delete an Online Endpoint.

        :param name: Name of the endpoint.
        :type name: str
        :param local: Whether to interact with the endpoint in local Docker environment. Defaults to False.
        :type local: bool
        :return: A poller to track the operation status if remote, else returns None if local.
        :rtype: Optional[LROPoller]
        """
        if local:
            return self._local_endpoint_helper.delete(name=name)

        start_time = time.time()
        path_format_arguments = {
            "endpointName": name,
            "resourceGroupName": self._resource_group_name,
            "workspaceName": self._workspace_name,
        }
        no_wait = kwargs.get("no_wait", False)

        delete_poller = self._online_operation.begin_delete(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            polling=AzureMLPolling(
                LROConfigurations.POLL_INTERVAL,
                path_format_arguments=path_format_arguments,
                **self._init_kwargs,
            )
            if not no_wait
            else False,
            polling_interval=LROConfigurations.POLL_INTERVAL,
            **self._init_kwargs,
        )
        if no_wait:
            module_logger.info(
                f"Delete request initiated. Status can be checked using `az ml online-endpoint show -n {name}`\n"
            )
            return delete_poller
        else:
            message = f"Deleting endpoint {name} \n"
            polling_wait(poller=delete_poller, start_time=start_time, message=message)

    @monitor_with_activity(logger, "OnlineEndpoint.BeginDeleteOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, endpoint: OnlineEndpoint, local: bool = False, **kwargs: Any) -> LROPoller:
        """Create or update an endpoint

        :param endpoint: The endpoint entity.
        :type endpoint: Endpoint
        :param local: Whether to interact with the endpoint in local Docker environment. Defaults to False.
        :type local: bool
        :return: A poller to track the operation status if remote, else returns None if local.
        :rtype: LROPoller
        """
        if local:
            return self._local_endpoint_helper.create_or_update(endpoint=endpoint)

        no_wait = kwargs.get("no_wait", False)
        try:
            location = self._get_workspace_location()

            if endpoint.traffic:
                endpoint.traffic = _strip_zeroes_from_traffic(endpoint.traffic)

            if endpoint.mirror_traffic:
                endpoint.mirror_traffic = _strip_zeroes_from_traffic(endpoint.mirror_traffic)

            endpoint_resource = endpoint._to_rest_online_endpoint(location=location)
            orchestrators = OperationOrchestrator(
                operation_container=self._all_operations, operation_scope=self._operation_scope
            )
            if hasattr(endpoint_resource.properties, "compute"):
                endpoint_resource.properties.compute = orchestrators.get_asset_arm_id(
                    endpoint_resource.properties.compute, azureml_type=AzureMLResourceType.COMPUTE
                )
            poller = self._online_operation.begin_create_or_update(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=endpoint.name,
                body=endpoint_resource,
                polling=not no_wait,
                **self._init_kwargs,
            )
            if no_wait:
                module_logger.info(
                    f"Endpoint Create/Update request initiated. Status can be checked using `az ml online-endpoint show -n {endpoint.name}`\n"
                )
                return poller
            else:
                return OnlineEndpoint._from_rest_object(poller.result())

        except Exception as ex:
            raise ex

    @monitor_with_activity(logger, "OnlineEndpoint.BeginGenerateKeys", ActivityType.PUBLICAPI)
    def begin_regenerate_keys(
        self, name: str, key_type: str = EndpointKeyType.PRIMARY_KEY_TYPE, **kwargs: Any
    ) -> LROPoller:
        """Regenerate keys for endpoint

        :param name: The endpoint name.
        :type name: The endpoint type. Defaults to ONLINE_ENDPOINT_TYPE.
        :param key_type: One of "primary", "secondary". Defaults to "primary".
        :type key_type: str
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        endpoint = self._online_operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            **self._init_kwargs,
        )

        no_wait = kwargs.get("no_wait", False)
        if endpoint.properties.auth_mode.lower() == "key":
            return self._regenerate_online_keys(name=name, key_type=key_type, no_wait=no_wait)
        else:
            raise ValidationException(
                message=f"Endpoint '{name}' does not use keys for authentication.",
                target=ErrorTarget.ONLINE_ENDPOINT,
                no_personal_data_message="Endpoint does not use keys for authentication.",
                error_category=ErrorCategory.USER_ERROR,
            )

    @monitor_with_activity(logger, "OnlineEndpoint.Invoke", ActivityType.PUBLICAPI)
    def invoke(
        self,
        endpoint_name: str,
        request_file: str = None,
        deployment_name: str = None,
        input_data: Union[str, Data] = None,
        params_override=None,
        local: bool = False,
        **kwargs,
    ) -> str:
        """Invokes the endpoint with the provided payload


        :param str endpoint_name: the endpoint name
        :param (str, optional) request_file: File containing the request payload. This is only valid for online endpoint.
        :param (str, optional) deployment_name: Name of a specific deployment to invoke. This is optional. By default requests are routed to any of the deployments according to the traffic rules.
        :param (Union[str, Data], optional) input_data: To use a pre-registered data asset, pass str in format
        :param (bool, optional) local: a flag to indicate whether to interact with endpoints in local Docker environment. Default: False.
        Returns:
            str: Prediction output for online endpoint.
        """
        params_override = params_override or []
        # Until this bug is resolved https://msdata.visualstudio.com/Vienna/_workitems/edit/1446538
        if deployment_name:
            self._validate_deployment_name(endpoint_name, deployment_name)

        with open(request_file, "rb") as f:
            data = json.loads(f.read())
        if local:
            return self._local_endpoint_helper.invoke(
                endpoint_name=endpoint_name, data=data, deployment_name=deployment_name
            )
        endpoint = self._online_operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint_name,
            **self._init_kwargs,
        )
        keys = self._get_online_credentials(name=endpoint_name, auth_mode=endpoint.properties.auth_mode)
        if isinstance(keys, EndpointAuthKeys):
            key = keys.primary_key
        elif isinstance(keys, EndpointAuthToken):
            key = keys.access_token
        else:
            key = ""
        headers = EndpointInvokeFields.DEFAULT_HEADER
        if key:
            headers[EndpointInvokeFields.AUTHORIZATION] = f"Bearer {key}"
        if deployment_name:
            headers[EndpointInvokeFields.MODEL_DEPLOYMENT] = deployment_name
        response = post_and_validate_response(endpoint.properties.scoring_uri, json=data, headers=headers, **kwargs)
        return response.text

    def _get_workspace_location(self) -> str:
        return self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location

    def _get_online_credentials(self, name: str, auth_mode: str = None) -> Union[EndpointAuthKeys, EndpointAuthToken]:
        if not auth_mode:
            endpoint = self._online_operation.get(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                **self._init_kwargs,
            )
            auth_mode = endpoint.properties.auth_mode
        if auth_mode.lower() == KEY:
            return self._online_operation.list_keys(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                **self._init_kwargs,
            )
        else:
            return self._online_operation.get_token(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                **self._init_kwargs,
            )

    def _regenerate_online_keys(
        self, name: str, key_type: str = EndpointKeyType.PRIMARY_KEY_TYPE, no_wait: bool = False
    ) -> Union[LROPoller[None], None]:
        keys = self._online_operation.list_keys(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            **self._init_kwargs,
        )
        if key_type.lower() == EndpointKeyType.PRIMARY_KEY_TYPE:
            key_request = RegenerateEndpointKeysRequest(key_type=KeyType.Primary, key_value=keys.primary_key)
        elif key_type.lower() == EndpointKeyType.SECONDARY_KEY_TYPE:
            key_request = RegenerateEndpointKeysRequest(key_type=KeyType.Secondary, key_value=keys.secondary_key)
        else:
            msg = "Key type must be 'primary' or 'secondary'."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.ONLINE_ENDPOINT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        poller = self._online_operation.begin_regenerate_keys(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            body=key_request,
            **self._init_kwargs,
        )
        if not no_wait:
            return polling_wait(poller=poller, message="regenerate key")
        else:
            return poller

    def _validate_deployment_name(self, endpoint_name, deployment_name):
        deployments_list = self._online_deployment_operation.list(
            endpoint_name=endpoint_name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [obj.name for obj in objs],
            **self._init_kwargs,
        )

        if deployments_list:
            if deployment_name not in deployments_list:
                raise ValidationException(
                    message=f"Deployment name {deployment_name} not found for this endpoint",
                    target=ErrorTarget.ONLINE_ENDPOINT,
                    no_personal_data_message="Deployment name not found for this endpoint",
                    error_category=ErrorCategory.USER_ERROR,
                )
        else:
            msg = "No deployment exists for this endpoint"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.ONLINE_ENDPOINT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
