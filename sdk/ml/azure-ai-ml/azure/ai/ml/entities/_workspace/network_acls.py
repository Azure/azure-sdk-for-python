# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from azure.ai.ml._restclient.v2024_10_01_preview.models import IPRule as RestIPRule
from azure.ai.ml._restclient.v2024_10_01_preview.models import NetworkAcls as RestNetworkAcls
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class IPRule(RestTranslatableMixin):

    def __init__(self, value: Optional[str]):
        self.value = value

    def __repr__(self):
        return f"IPRule(value={self.value})"

    def _to_rest_object(self) -> RestIPRule:
        return RestIPRule(value=self.value)

    @classmethod
    def _from_rest_object(cls, obj: RestIPRule) -> "IPRule":
        return cls(value=obj.value)


class DefaultActionType:

    DENY = "Deny"
    ALLOW = "Allow"


class NetworkAcls(RestTranslatableMixin):

    def __init__(
        self,
        *,
        default_action: str = DefaultActionType.ALLOW,
        ip_rules: Optional[List[IPRule]] = None,
    ):
        self.default_action = default_action
        self.ip_rules = ip_rules if ip_rules is not None else []

    def __repr__(self):
        ip_rules_repr = ", ".join(repr(ip_rule) for ip_rule in self.ip_rules)
        return f"NetworkAcls(default_action={self.default_action}, ip_rules=[{ip_rules_repr}])"

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
            default_action=obj.default_action,
            ip_rules=(
                [IPRule._from_rest_object(ip_rule) for ip_rule in obj.ip_rules]  # pylint: disable=protected-access
                if obj.ip_rules
                else []
            ),
        )
