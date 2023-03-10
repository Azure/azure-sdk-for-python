# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Iterable, Optional

from azure.ai.ml._scope_dependent_operations import OperationScope

from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml._utils.azure_resource_utils import (
    get_virtual_clusters_from_subscriptions,
    get_virtual_cluster_by_name,
    get_generic_resource_by_id
)
from azure.ai.ml.constants._common import Scope
from azure.ai.ml.exceptions import UserErrorException
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import TokenCredential
from azure.ai.ml._utils._arm_id_utils import AzureResourceId

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class VirtualClusterOperations:
    """VirtualClusterOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        credentials: TokenCredential,
        **kwargs: Dict,
    ):
        ops_logger.update_info(kwargs)
        self._resource_group_name = operation_scope.resource_group_name
        self._subscription_id = operation_scope.subscription_id
        self._credentials = credentials
        self._init_kwargs = kwargs

    @distributed_trace
    @monitor_with_activity(logger, "VirtualCluster.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: Optional[str] = None) -> Iterable[Dict]:
        """List virtual clusters a user has access to.

        :param scope: scope of the listing, "subscription" or None, defaults to None.
            If None, list virtual clusters across all subscriptions a customer has access to.
        :type scope: str, optional
        :return: An iterator like instance of dictionaries.
        :rtype: ~azure.core.paging.ItemPaged[Dict]
        """

        if scope is None:
            subscription_list = None
        elif scope.lower() == Scope.SUBSCRIPTION:
            subscription_list = [self._subscription_id]
        else:
            message = f"Invalid scope: {scope}. Valid values are 'subscription' or None."
            raise UserErrorException(message=message, no_personal_data_message=message)

        return get_virtual_clusters_from_subscriptions(self._credentials, subscription_list=subscription_list)

    @distributed_trace
    @monitor_with_activity(logger, "VirtualCluster.Get", ActivityType.PUBLICAPI)
    def get(self, name: str) -> Dict:
        """
        Get a virtual cluster resource. If name is provided, the virtual cluster
        with the name in the subscription and resource group of the MLClient object
        will be returned. If an ARM id is provided, a virtual cluster with the id will be returned.

        :param name: Name or ARM ID of the virtual cluster.
        :type name: str
        :return: Virtual cluster object
        :rtype: Dict
        """

        try :
            arm_id = AzureResourceId(name)
            sub_id = arm_id.subscription_id

            return get_generic_resource_by_id(arm_id=name, credential=self._credentials, subscription_id=sub_id)
        except ValidationException:
            return get_virtual_cluster_by_name(
                name=name,
                resource_group=self._resource_group_name,
                subscription_id=self._subscription_id,
                credential=self._credentials,
            )
