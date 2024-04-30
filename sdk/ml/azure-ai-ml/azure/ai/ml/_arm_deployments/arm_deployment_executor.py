# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
import time
from typing import Any, Dict, Optional

from azure.ai.ml._arm_deployments.arm_helper import deployment_message_mapping
from azure.ai.ml._azure_environments import (
    _get_azure_portal_id_from_metadata,
    _get_base_url_from_metadata,
    _get_cloud_details,
    _resource_to_scopes,
)
from azure.ai.ml._utils._arm_id_utils import AzureResourceId, get_arm_id_object_from_id
from azure.ai.ml._utils._logger_utils import initialize_logger_info
from azure.ai.ml._utils.utils import from_iso_duration_format_min_sec
from azure.ai.ml._vendor.azure_resources._resource_management_client import ResourceManagementClient
from azure.ai.ml._vendor.azure_resources.models import Deployment, DeploymentProperties
from azure.ai.ml.constants._common import (
    ENDPOINT_DEPLOYMENT_START_MSG,
    ArmConstants,
    LROConfigurations,
    OperationStatus,
)
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="")


# pylint: disable=too-many-instance-attributes
class ArmDeploymentExecutor(object):
    def __init__(
        self,
        credentials: TokenCredential,
        resource_group_name: str,
        subscription_id: str,
        deployment_name: str,
        **kwargs,
    ):
        self._credentials = credentials
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._deployment_name = deployment_name
        self._cloud = _get_cloud_details()
        management_hostname = _get_base_url_from_metadata()
        credential_scopes = _resource_to_scopes(management_hostname)
        kwargs.pop("base_url", None)
        if credential_scopes is not None:
            kwargs["credential_scopes"] = credential_scopes
        self._client = ResourceManagementClient(
            credential=self._credentials,
            subscription_id=self._subscription_id,
            api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
            base_url=management_hostname,
            **kwargs,
        )
        self._deployment_operations_client = self._client.deployment_operations
        self._deployments_client = self._client.deployments
        self._deployment_tracking = []
        self._lock = None  # To allow only one deployment to print
        self._printed_set = set()  # To prevent already printed deployment from re using the console
        self._resources_being_deployed = {}

    def deploy_resource(
        self,
        template: str,
        resources_being_deployed: Dict[str, Any],
        parameters: Optional[Dict] = None,
        wait: bool = True,
    ) -> Optional[LROPoller]:
        total_duration = None
        if not resources_being_deployed:
            msg = "No resource is being deployed. Please check the template again."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.ARM_DEPLOYMENT,
                error_category=ErrorCategory.USER_ERROR,
            )
        error = None
        # pylint: disable=too-many-nested-blocks
        try:
            poller = self._get_poller(template=template, parameters=parameters)
            module_logger.info(
                "The deployment request %s was accepted. ARM deployment URI for reference: \n", self._deployment_name
            )
            endpoint_deployment_start_message = ENDPOINT_DEPLOYMENT_START_MSG.format(
                _get_azure_portal_id_from_metadata(),
                self._subscription_id,
                self._resource_group_name,
                self._deployment_name,
            )
            module_logger.info(endpoint_deployment_start_message)
            if wait:
                try:
                    while not poller.done():
                        try:
                            time.sleep(LROConfigurations.SLEEP_TIME)
                            self._check_deployment_status()
                        except KeyboardInterrupt as e:
                            self._client.close()
                            error = e
                            raise

                    if poller._exception is not None:
                        error = poller._exception
                except Exception as e:  # pylint: disable=W0718
                    error = e
                finally:
                    # one last check to make sure all print statements make it
                    if not isinstance(error, KeyboardInterrupt):
                        self._check_deployment_status()
                        total_duration = poller.result().properties.duration
            else:
                return poller
        except Exception as ex:
            module_logger.debug("Polling hit the exception %s\n", ex)
            raise ex

        if error is not None:
            error_msg = f"Unable to create resource. \n {error}\n"
            module_logger.error(error_msg)
            raise error
        if len(resources_being_deployed) > 1 and total_duration:
            module_logger.info("Total time : %s\n", from_iso_duration_format_min_sec(total_duration))
        return None

    def _get_poller(self, template: str, parameters: Optional[Dict] = None, wait: bool = True) -> None:
        # deploy the template
        properties = DeploymentProperties(template=template, parameters=parameters, mode="incremental")
        return self._deployments_client.begin_create_or_update(
            resource_group_name=self._resource_group_name,
            deployment_name=self._deployment_name,
            parameters=Deployment(properties=properties),
            polling=wait,
            polling_interval=LROConfigurations.POLL_INTERVAL,
        )

    # pylint: disable=too-many-statements
    def _check_deployment_status(self) -> None:
        deployment_operations = self._deployment_operations_client.list(
            resource_group_name=self._resource_group_name,
            deployment_name=self._deployment_name,
        )

        for deployment_operation in deployment_operations:
            operation_id = deployment_operation.operation_id
            properties = deployment_operation.properties
            target_resource = properties.target_resource

            module_logger.debug(
                "\n Received deployment operation: %s, with status %s\n\n",
                target_resource,
                properties.provisioning_state,
            )

            if properties.provisioning_operation == "EvaluateDeploymentOutput":
                continue

            arm_id_obj = get_arm_id_object_from_id(target_resource.id)

            resource_name = (
                f"{arm_id_obj.asset_name} {arm_id_obj.asset_version if hasattr(arm_id_obj,'asset_version') else ''}"
            )
            # do swap on asset_type to avoid collision with workspaces asset_type in arm id
            if isinstance(arm_id_obj, AzureResourceId):
                arm_id_obj.asset_type = (
                    arm_id_obj.asset_type
                    if not arm_id_obj.provider_namespace_with_type == "OperationalInsightsworkspaces"
                    else "LogAnalytics"
                )
            deployment_message = deployment_message_mapping[arm_id_obj.asset_type].format(f"{resource_name} ")
            if target_resource.resource_name not in self._resources_being_deployed:
                self._resources_being_deployed[target_resource.resource_name] = (
                    deployment_message,
                    None,
                )

            if (
                properties.provisioning_state
                and (not self._lock or self._lock == target_resource.resource_name)
                and target_resource.resource_name not in self._printed_set
            ):
                status_in_resource_dict = self._resources_being_deployed[target_resource.resource_name][1]
                module_logger.debug(
                    ("\n LOCK STATUS :  %s,  Status in the resources dict : %s ,  Already in printed set: %s\n"),
                    self._lock,
                    status_in_resource_dict,
                    self._printed_set,
                )
                module_logger.debug("Locking with the deployment : %s\n\n", target_resource.resource_name)
                self._lock = target_resource.resource_name
                provisioning_state = properties.provisioning_state
                request_id = properties.service_request_id

                if target_resource is None:
                    continue

                resource_name = target_resource.resource_name
                if resource_name not in self._resources_being_deployed:
                    resource_type, previous_state = resource_name, None
                else:
                    resource_type, previous_state = self._resources_being_deployed[resource_name]

                duration = properties.duration
                # duration comes in format: "PT1M56.3454108S"
                try:
                    duration_in_min_sec = from_iso_duration_format_min_sec(duration)
                except Exception:  # pylint: disable=W0718
                    duration_in_min_sec = ""

                self._resources_being_deployed[resource_name] = (
                    resource_type,
                    provisioning_state,
                )

                if provisioning_state == OperationStatus.FAILED and previous_state != OperationStatus.FAILED:
                    status_code = properties.status_code
                    status_message = properties.status_message
                    module_logger.debug(
                        (
                            "%s: Failed with operation id= %s, "
                            "service request id=%s, status=%s, "
                            "error message = %s.\n"
                        ),
                        resource_type,
                        operation_id,
                        request_id,
                        status_code,
                        status_message.error,
                    )
                    module_logger.debug(
                        "More details: %s\n",
                        status_message.error.details[0].message if status_message.error.details else None,
                    )
                    # self._lock = None
                # First time we're seeing this so let the user know it's being deployed
                elif properties.provisioning_state == OperationStatus.RUNNING and previous_state is None:
                    module_logger.info("%s ", resource_type)
                elif (
                    properties.provisioning_state == OperationStatus.RUNNING
                    and previous_state == OperationStatus.RUNNING
                ):
                    module_logger.info(".")
                # If the provisioning has already succeeded but we hadn't seen it Running before
                # (really quick deployment - so probably never happening) let user know resource
                # is being deployed and then let user know it has been deployed
                elif properties.provisioning_state == OperationStatus.SUCCEEDED and previous_state is None:
                    module_logger.info("%s  Done (%s)\n", resource_type, duration_in_min_sec)
                    self._lock = None
                    self._printed_set.add(resource_name)
                    module_logger.debug("Releasing lock for deployment: %s\n\n", target_resource.resource_name)
                # Finally, deployment has succeeded and was previously running, so mark it as finished
                elif (
                    properties.provisioning_state == OperationStatus.SUCCEEDED
                    and previous_state != OperationStatus.SUCCEEDED
                ):
                    module_logger.info("  Done (%s)\n", duration_in_min_sec)
                    self._lock = None
                    self._printed_set.add(resource_name)
                    module_logger.debug("Releasing lock for deployment: %s\n\n", target_resource.resource_name)
