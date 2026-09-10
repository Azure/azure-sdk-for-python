# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._assets import IPProtectionLevel
from azure.ai.ml.entities._mixins import RestTranslatableMixin


@experimental
class IntellectualProperty(RestTranslatableMixin):
    """Intellectual property settings definition.

    :keyword publisher: The publisher's name.
    :paramtype publisher: Optional[str]
    :keyword protection_level: Asset Protection Level. Accepted values are IPProtectionLevel.ALL ("all") and
        IPProtectionLevel.NONE ("none"). Defaults to IPProtectionLevel.ALL ("all").
    :paramtype protection_level: Optional[Union[str, ~azure.ai.ml.constants.IPProtectionLevel]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START intellectual_property_configuration]
            :end-before: [END intellectual_property_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring intellectual property settings on a CommandComponent.
    """

    def __init__(
        self, *, publisher: Optional[str] = None, protection_level: IPProtectionLevel = IPProtectionLevel.ALL
    ) -> None:
        self.publisher = publisher
        self.protection_level = protection_level

    def _to_rest_object(self) -> Dict[str, Any]:
        # ``IntellectualProperty`` was dropped from the arm_ml_service (2025-12) model; build the
        # 2023-04 wire body directly as a dict (JSON-direct).
        return {"publisher": self.publisher, "protectionLevel": self.protection_level}

    @classmethod
    def _from_rest_object(cls, obj: Any) -> "IntellectualProperty":
        publisher = obj.get("publisher") if hasattr(obj, "get") else obj.publisher
        protection_level = obj.get("protectionLevel") if hasattr(obj, "get") else obj.protection_level
        return cls(publisher=publisher, protection_level=protection_level)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IntellectualProperty):
            return NotImplemented
        return self.publisher == other.publisher and self.protection_level == other.protection_level
