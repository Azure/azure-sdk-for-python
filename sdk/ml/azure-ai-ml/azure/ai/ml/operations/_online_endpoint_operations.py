# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
from typing import Any, Dict, Optional, Union

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._azure_environments import _resource_to_scopes
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2022_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022022Preview
from azure.ai.ml._restclient.v2022_02_01_preview.models import KeyType, RegenerateEndpointKeysRequest
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._azureml_polling import AzureMLPolling
from azure.ai.ml._utils._endpoint_utils import validate_response
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import (
    AAD_TOKEN,
    AAD_TOKEN_RESOURCE_ENDPOINT,
    EMPTY_CREDENTIALS_ERROR,
    KEY,
    AzureMLResourceType,
    LROConfigurations,
)
from azure.ai.ml.constants._endpoint import EndpointInvokeFields, EndpointKeyType
from azure.ai.ml.entities import OnlineDeployment, OnlineEndpoint
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._endpoint.online_endpoint import EndpointAadToken, EndpointAuthKeys, EndpointAuthToken
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationErrorType, ValidationException
from azure.ai.ml.operations._local_endpoint_helper import _LocalEndpointHelper
from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


def _strip_zeroes_from_traffic(traffic: Dict[str, str]) -> Dict[str, str]:
    return {k.lower(): v for k, v in traffic.items() if v and int(v) != 0}


class OnlineEndpointOperations(_ScopeDependentOperations):
    """OnlineEndpointOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client_02_2022_preview: ServiceClient022022Preview,
        all_operations: OperationsContainer,
        local_endpoint_helper: _LocalEndpointHelper,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        super(OnlineEndpointOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._online_operation = service_client_02_2022_preview.online_endpoints
        self._online_deployment_operation = service_client_02_2022_preview.online_deployments
        self._all_operations = all_operations
        self._local_endpoint_helper = local_endpoint_helper
        self._credentials = credentials
        self._init_kwargs = kwargs

        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")

    @distributed_trace
    @monitor_with_activity(ops_logger, "OnlineEndpoint.List", ActivityType.PUBLICAPI)
    def list(self, *, local: bool = False) -> ItemPaged[OnlineEndpoint]:
        """List endpoints of the workspace.

        :keyword local: (Optional) Flag to indicate whether to interact with endpoints in local Docker environment.
            Default: False
        :type local: bool
        :return: A list of endpoints
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.OnlineEndpoint]
        """
        if local:
            return self._local_endpoint_helper.list()
        return self._online_operation.list(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [OnlineEndpoint._from_rest_object(obj) for obj in objs],
            **self._init_kwargs,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "OnlineEndpoint.ListKeys", ActivityType.PUBLICAPI)
    def get_keys(self, name: str) -> Union[EndpointAuthKeys, EndpointAuthToken, EndpointAadToken]:
        """Get the auth credentials.

        :param name: The endpoint name
        :type name: str
        :raise: Exception if cannot get online credentials
        :return: Depending on the auth mode in the endpoint, returns either keys or token
        :rtype: Union[~azure.ai.ml.entities.EndpointAuthKeys, ~azure.ai.ml.entities.EndpointAuthToken]
        """
        return self._get_online_credentials(name=name)

    @distributed_trace
    @monitor_with_activity(ops_logger, "OnlineEndpoint.Get", ActivityType.PUBLICAPI)
    def get(
        self,
        name: str,
        *,
        local: bool = False,
    ) -> OnlineEndpoint:
        """Get a Endpoint resource.

        :param name: Name of the endpoint.
        :type name: str
        :keyword local: Indicates whether to interact with endpoints in local Docker environment. Defaults to False.
        :paramtype local: Optional[bool]
        :raises ~azure.ai.ml.exceptions.LocalEndpointNotFoundError: Raised if local endpoint resource does not exist.
        :return: Endpoint object retrieved from the service.
        :rtype: ~azure.ai.ml.entities.OnlineEndpoint
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

    @distributed_trace
    @monitor_with_activity(ops_logger, "OnlineEndpoint.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: Optional[str] = None, *, local: bool = False) -> LROPoller[None]:
        """Delete an Online Endpoint.

        :param name: Name of the endpoint.
        :type name: str
        :keyword local: Whether to interact with the endpoint in local Docker environment. Defaults to False.
        :paramtype local: bool
        :raises ~azure.ai.ml.exceptions.LocalEndpointNotFoundError: Raised if local endpoint resource does not exist.
        :return: A poller to track the operation status if remote, else returns None if local.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        if local:
            return self._local_endpoint_helper.delete(name=str(name))

        path_format_arguments = {
            "endpointName": name,
            "resourceGroupName": self._resource_group_name,
            "workspaceName": self._workspace_name,
        }

        delete_poller = self._online_operation.begin_delete(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            polling=AzureMLPolling(
                LROConfigurations.POLL_INTERVAL,
                path_format_arguments=path_format_arguments,
                **self._init_kwargs,
            ),
            polling_interval=LROConfigurations.POLL_INTERVAL,
            **self._init_kwargs,
        )
        return delete_poller

    @distributed_trace
    @monitor_with_activity(ops_logger, "OnlineEndpoint.BeginDeleteOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, endpoint: OnlineEndpoint, *, local: bool = False) -> LROPoller[OnlineEndpoint]:
        """Create or update an endpoint.

        :param endpoint: The endpoint entity.
        :type endpoint: ~azure.ai.ml.entities.OnlineEndpoint
        :keyword local: Whether to interact with the endpoint in local Docker environment. Defaults to False.
        :paramtype local: bool
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if OnlineEndpoint cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.AssetException: Raised if OnlineEndpoint assets
            (e.g. Data, Code, Model, Environment) cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.ModelException: Raised if OnlineEndpoint model cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :raises ~azure.ai.ml.exceptions.LocalEndpointNotFoundError: Raised if local endpoint resource does not exist.
        :return: A poller to track the operation status if remote, else returns None if local.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.OnlineEndpoint]
        """
        try:
            if local:
                return self._local_endpoint_helper.create_or_update(endpoint=endpoint)

            try:
                location = self._get_workspace_location()

                if endpoint.traffic:
                    endpoint.traffic = _strip_zeroes_from_traffic(endpoint.traffic)

                if endpoint.mirror_traffic:
                    endpoint.mirror_traffic = _strip_zeroes_from_traffic(endpoint.mirror_traffic)

                endpoint_resource = endpoint._to_rest_online_endpoint(location=location)
                orchestrators = OperationOrchestrator(
                    operation_container=self._all_operations,
                    operation_scope=self._operation_scope,
                    operation_config=self._operation_config,
                )
                if hasattr(endpoint_resource.properties, "compute"):
                    endpoint_resource.properties.compute = orchestrators.get_asset_arm_id(
                        endpoint_resource.properties.compute,
                        azureml_type=AzureMLResourceType.COMPUTE,
                    )
                poller = self._online_operation.begin_create_or_update(
                    resource_group_name=self._resource_group_name,
                    workspace_name=self._workspace_name,
                    endpoint_name=endpoint.name,
                    body=endpoint_resource,
                    cls=lambda response, deserialized, headers: OnlineEndpoint._from_rest_object(deserialized),
                    **self._init_kwargs,
                )
                return poller

            except Exception as ex:
                raise ex
        except Exception as ex:  # pylint: disable=W0718
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            else:
                raise ex

    @distributed_trace
    @monitor_with_activity(ops_logger, "OnlineEndpoint.BeginGenerateKeys", ActivityType.PUBLICAPI)
    def begin_regenerate_keys(
        self,
        name: str,
        *,
        key_type: str = EndpointKeyType.PRIMARY_KEY_TYPE,
    ) -> LROPoller[None]:
        """Regenerate keys for endpoint.

        :param name: The endpoint name.
        :type name: The endpoint type. Defaults to ONLINE_ENDPOINT_TYPE.
        :keyword key_type: One of "primary", "secondary". Defaults to "primary".
        :paramtype key_type: str
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        endpoint = self._online_operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            **self._init_kwargs,
        )

        if endpoint.properties.auth_mode.lower() == "key":
            return self._regenerate_online_keys(name=name, key_type=key_type)

        raise ValidationException(
            message=f"Endpoint '{name}' does not use keys for authentication.",
            target=ErrorTarget.ONLINE_ENDPOINT,
            no_personal_data_message="Endpoint does not use keys for authentication.",
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "OnlineEndpoint.Invoke", ActivityType.PUBLICAPI)
    def invoke(
        self,
        endpoint_name: str,
        *,
        request_file: Optional[str] = None,
        deployment_name: Optional[str] = None,
        # pylint: disable=unused-argument
        input_data: Optional[Union[str, Data]] = None,
        params_override: Any = None,
        local: bool = False,
        # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> str:
        """Invokes the endpoint with the provided payload.

        :param endpoint_name: The endpoint name
        :type endpoint_name: str
        :keyword request_file: File containing the request payload. This is only valid for online endpoint.
        :paramtype request_file: Optional[str]
        :keyword deployment_name: Name of a specific deployment to invoke. This is optional.
            By default requests are routed to any of the deployments according to the traffic rules.
        :paramtype deployment_name: Optional[str]
        :keyword input_data: To use a pre-registered data asset, pass str in format
        :paramtype input_data: Optional[Union[str, Data]]
        :keyword params_override: A dictionary of payload parameters to override and their desired values.
        :paramtype params_override: Any
        :keyword local: Indicates whether to interact with endpoints in local Docker environment. Defaults to False.
        :paramtype local: Optional[bool]
        :raises ~azure.ai.ml.exceptions.LocalEndpointNotFoundError: Raised if local endpoint resource does not exist.
        :raises ~azure.ai.ml.exceptions.MultipleLocalDeploymentsFoundError: Raised if there are multiple deployments
            and no deployment_name is specified.
        :raises ~azure.ai.ml.exceptions.InvalidLocalEndpointError: Raised if local endpoint is None.
        :return: Prediction output for online endpoint.
        :rtype: str
        """
        params_override = params_override or []
        # Until this bug is resolved https://msdata.visualstudio.com/Vienna/_workitems/edit/1446538
        if deployment_name:
            self._validate_deployment_name(endpoint_name, deployment_name)

        with open(request_file, "rb") as f:  # type: ignore[arg-type]
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
        elif isinstance(keys, (EndpointAuthToken, EndpointAadToken)):
            key = keys.access_token
        else:
            key = ""
        headers = EndpointInvokeFields.DEFAULT_HEADER
        if key:
            headers[EndpointInvokeFields.AUTHORIZATION] = f"Bearer {key}"
        if deployment_name:
            headers[EndpointInvokeFields.MODEL_DEPLOYMENT] = deployment_name

        response = self._requests_pipeline.post(endpoint.properties.scoring_uri, json=data, headers=headers)
        validate_response(response)
        return str(response.text())

    def _get_workspace_location(self) -> str:
        return str(
            self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location
        )

    def _get_online_credentials(
        self, name: str, auth_mode: Optional[str] = None
    ) -> Union[EndpointAuthKeys, EndpointAuthToken, EndpointAadToken]:
        if not auth_mode:
            endpoint = self._online_operation.get(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                **self._init_kwargs,
            )
            auth_mode = endpoint.properties.auth_mode
        if auth_mode is not None and auth_mode.lower() == KEY:
            return self._online_operation.list_keys(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                # pylint: disable=protected-access
                cls=lambda x, response, z: EndpointAuthKeys._from_rest_object(response),
                **self._init_kwargs,
            )

        if auth_mode is not None and auth_mode.lower() == AAD_TOKEN:
            if self._credentials:
                return EndpointAadToken(self._credentials.get_token(*_resource_to_scopes(AAD_TOKEN_RESOURCE_ENDPOINT)))
            msg = EMPTY_CREDENTIALS_ERROR
            raise MlException(message=msg, no_personal_data_message=msg)

        return self._online_operation.get_token(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            # pylint: disable=protected-access
            cls=lambda x, response, z: EndpointAuthToken._from_rest_object(response),
            **self._init_kwargs,
        )

    def _regenerate_online_keys(
        self,
        name: str,
        key_type: str = EndpointKeyType.PRIMARY_KEY_TYPE,
    ) -> LROPoller[None]:
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
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        poller = self._online_operation.begin_regenerate_keys(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            body=key_request,
            **self._init_kwargs,
        )

        return poller

    def _validate_deployment_name(self, endpoint_name: str, deployment_name: str) -> None:
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
                    error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
                )
        else:
            msg = "No deployment exists for this endpoint"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.ONLINE_ENDPOINT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
            )
