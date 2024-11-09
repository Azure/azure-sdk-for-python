# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from azure.ai.ml._restclient.v2024_10_01_preview.models import IPRule as RestIPRule
from azure.ai.ml._restclient.v2024_10_01_preview.models import NetworkAcls as RestNetworkAcls
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class NetworkAcls(RestTranslatableMixin):
    class IPRule(RestTranslatableMixin):
        """Represents an IP rule with a value.

        :param value: An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address)
        or '124.56.78.0/24' (all addresses that start with 124.56.78). Value could be 'Allow' or 'Deny'.
        :type value: str
        """

        def __init__(self, value: Optional[str]):
            self.value = value

        def __repr__(self):
            return f"IPRule(value={self.value})"

        def _to_rest_object(self) -> RestIPRule:
            return RestIPRule(value=self.value)

        @classmethod
        def _from_rest_object(cls, obj: RestIPRule) -> "NetworkAcls.IPRule":
            return cls(value=obj.value)

    class DefaultActionType:
        """Specifies the default action when no IP rules are matched.
        'Deny' if IP rules are non-empty, allowing only specified IPs/ranges;
        'Allow' if no IP rules are defined, allowing all access.
        """

        DENY = "Deny"
        ALLOW = "Allow"

    def __init__(
        self,
        *,
        bypass: str = "",
        default_action: str = DefaultActionType.ALLOW,
        ip_rules: Optional[List[IPRule]] = None,
        resource_access_rules: Optional[List[str]] = None,
    ):
        """Initializes the NetworkAcls object.

        :param bypass: Specifies whether to bypass the default action.
        :type bypass: str
        :param ip_rules: Rules governing the accessibility of a resource from a specific IP address or IP range.
        :type ip_rules: Optional[List[IPRule]]
        :param resource_access_rules: Rules governing the accessibility of a resource.
        :type resource_access_rules: Optional[List[str]]
        """
        self.bypass = bypass
        self.ip_rules = ip_rules if ip_rules is not None else []
        self.default_action = default_action
        self.resource_access_rules = resource_access_rules if resource_access_rules is not None else []

    def _to_rest_object(self) -> RestNetworkAcls:
        return RestNetworkAcls(
            default_action=self.default_action,
            ip_rules=(
                [ip_rule._to_rest_object() for ip_rule in self.ip_rules]  # pylint: disable=protected-access
                if self.ip_rules
                else None
            ),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestNetworkAcls) -> "NetworkAcls":
        return cls(
            ip_rules=(
                [
                    NetworkAcls.IPRule._from_rest_object(ip_rule)  # pylint: disable=protected-access
                    for ip_rule in obj.ip_rules
                ]
                if obj.ip_rules
                else []
            ),
            default_action=obj.default_action,
        )
