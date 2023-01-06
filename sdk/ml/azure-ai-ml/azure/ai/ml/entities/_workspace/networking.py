# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional
#from azure.ai.ml._schema.workspace.networking import ManagedNetworkSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, WorkspaceResourceConstants


class IsolationMode:
    disabled = "Disabled"
    allow_internet_outbound = "AllowInternetOutbound"
    allow_only_approved_outbound = "AllowOnlyApprovedOutbound"


class Protocol:
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    ALL = "*"


class OutboundRuleCategory:
    required = "Required"
    recommended = "Recommended"
    user_defined = "UserDefined"


class OutboundRuleType:
    fqdn = "FQDN"
    private_endpoint = "PrivateEndpoint"
    service_tag = "ServiceTag"


class OutboundRule:
    def __init__(
        self,
        type: str = None
    ) -> None:
        self.type = type
        self.category = OutboundRuleCategory.user_defined
        

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "OutboundRule":
        return ManagedNetwork()


class FqdnDestination(OutboundRule):
    def __init__(self, destination: str) -> None:
        self.destination = destination
        OutboundRule.__init__(self, type=OutboundRuleType.fqdn)


class PrivateEndpointDestination(OutboundRule):
    def __init__(self, service_resource_id: str, subresource_target: str, spark_jobs_enabled: bool = False) -> None:
        self.service_resource_id = service_resource_id
        self.subresource_target = subresource_target
        self.spark_jobs_enabled = spark_jobs_enabled
        OutboundRule.__init__(self, OutboundRuleType.private_endpoint)


class ServiceTagDestination(OutboundRule):
    def __init__(self, service_tag: str, protocol: str, port_ranges: str) -> None:
        self.service_tag = service_tag
        self.protocol = protocol
        self.port_ranges = port_ranges
        OutboundRule.__init__(self, OutboundRuleType.service_tag)


class ManagedNetwork:
    def __init__(
        self,
        isolation_mode: str = IsolationMode.disabled, 
        outbound_rules: Optional[Dict[str, OutboundRule]] = None
    ) -> None:
        self.isolation_mode = isolation_mode
        self.outbound_rules = outbound_rules

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "ManagedNetwork":
        return ManagedNetwork()

    def _to_dict(self) -> Dict:
        return {
            "need": "to implement to_dict for ManagedNetwork"
        }
        # pylint: disable=no-member
        #return ManagedNetworkSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        # NEED TO return a dict of the object, which means need to create Schema object 
        # like above but cannot import schema due to circular import (schema imports
        # ManagedNetwork), what is the correct way to do this here?


    """@classmethod
    def _from_workspace_rest_object(cls, obj: RestManagedServiceIdentityConfiguration) -> "IdentityConfiguration":
        from_rest_user_assigned_identities = (
            [
                ManagedIdentityConfiguration._from_identity_configuration_rest_object(uai, resource_id=resource_id)
                for (resource_id, uai) in obj.user_assigned_identities.items()
            ]
            if obj.user_assigned_identities
            else None
        )
        result = cls(
            type=camel_to_snake(obj.type),
            user_assigned_identities=from_rest_user_assigned_identities,
        )
        result.principal_id = obj.principal_id
        result.tenant_id = obj.tenant_id
        return result

    def _to_workspace_rest_object(self) -> RestManagedServiceIdentityConfiguration:
        rest_user_assigned_identities = (
            {uai.resource_id: uai._to_workspace_rest_object() for uai in self.user_assigned_identities}
            if self.user_assigned_identities
            else None
        )
        return RestManagedServiceIdentityConfiguration(
            type=snake_to_pascal(self.type), user_assigned_identities=rest_user_assigned_identities
        )
"""