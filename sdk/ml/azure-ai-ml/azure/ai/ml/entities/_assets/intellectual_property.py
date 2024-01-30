# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import IntellectualProperty as RestIntellectualProperty
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

    def _to_rest_object(self) -> RestIntellectualProperty:
        return RestIntellectualProperty(publisher=self.publisher, protection_level=self.protection_level)

    @classmethod
    def _from_rest_object(cls, obj: RestIntellectualProperty) -> "IntellectualProperty":
        return cls(publisher=obj.publisher, protection_level=obj.protection_level)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IntellectualProperty):
            return NotImplemented
        return self.publisher == other.publisher and self.protection_level == other.protection_level
