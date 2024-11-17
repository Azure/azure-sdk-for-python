# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from azure.ai.ml._restclient.v2024_10_01_preview.models import IPRule as RestIPRule
from azure.ai.ml._restclient.v2024_10_01_preview.models import NetworkAcls as RestNetworkAcls
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class NetworkAcls(RestTranslatableMixin):

    class IPRule(RestTranslatableMixin):

        def __init__(self, value: Optional[str]):
            self.value = value

        def __repr__(self):
            return f"IPRule(value={self.value})"

        def _to_rest_object(self) -> RestIPRule:
            return RestIPRule(value=self.value)

        @classmethod
        def _from_rest_object(cls, obj: RestIPRule) -> "NetworkAcls.IPRule":
            return cls(value=obj.value)

    def __init__(
        self,
        *,
        ip_rules: Optional[List[IPRule]] = None,
    ):
        self.ip_rules = ip_rules if ip_rules is not None else []

    def _to_rest_object(self) -> RestNetworkAcls:
        return RestNetworkAcls(
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
        )
