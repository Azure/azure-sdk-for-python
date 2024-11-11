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
        default_action: str = DefaultActionType.ALLOW,
        ip_rules: Optional[List[IPRule]] = None,
    ):
        """Initializes the NetworkAcls object.

        :param bypass: Specifies whether to bypass the default action.
        :param ip_rules: Rules governing the accessibility of a resource from a specific IP address or IP range.
        :type ip_rules: Optional[List[IPRule]]
        :param resource_access_rules: Rules governing the accessibility of a resource.
        """
        self.ip_rules = ip_rules if ip_rules is not None else []
        self.default_action = default_action

    def __repr__(self):
        ip_rules_repr = ", ".join(repr(ip_rule) for ip_rule in self.ip_rules)
        return f"NetworkAcls(default_action={self.default_action}, " f"ip_rules=[{ip_rules_repr}])"

    def _to_rest_object(self) -> RestNetworkAcls:
        return RestNetworkAcls(
            default_action=self.default_action,
            ip_rules=(
                [ip_rule._to_rest_object() for ip_rule in self.ip_rules]  # pylint: disable=protected-access
                if self.ip_rules
                else None
            ),
        )

    def convert_to_ip_allowlist(self) -> List[str]:
        """Converts the IP rules to an IP allowlist.
        :return: A list of IP addresses or IP ranges.
        :rtype: List[str]
        """
        return [rule.value for rule in self.ip_rules if rule.value is not None]

    @classmethod
    def parse(cls, ip_allowlist: Optional[List[str]]) -> "NetworkAcls":
        """Parses a list of IP allowlist strings into a NetworkAcls object.
        :param ip_allowlist: A list of IP addresses or IP ranges in CIDR notation.
        :type ip_allowlist: Optional[List[str]]
        :return: A NetworkAcls object.
        :rtype: NetworkAcls
        """
        default_action = (
            NetworkAcls.DefaultActionType.DENY
            if ip_allowlist and len(ip_allowlist) > 0
            else NetworkAcls.DefaultActionType.ALLOW
        )
        ip_rules = [NetworkAcls.IPRule(value=ip) for ip in ip_allowlist] if ip_allowlist else []
        return cls(ip_rules=ip_rules, default_action=default_action)

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
