# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import IPProtectionLevel
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_04_01_preview.models import IntellectualProperty as RestIntellectualProperty

@experimental
class IntellectualProperty(RestTranslatableMixin):
    """ Class which defines the intellectual property settings.
    :param publisher: Publisher name
    :type publisher: str
    :param protection_level: Asset Protection Level. Allowed values: ALL, NONE
    :type protection_level: IPProtectionLevel
    """
    def __init__(
        self,
        *,
        publisher: str = None,
        protection_level: IPProtectionLevel = IPProtectionLevel.ALL
    ):
        self.publisher = publisher
        self.protection_level = protection_level

    def _to_rest_object(self) -> RestIntellectualProperty :
        return RestIntellectualProperty(
            publisher=self.publisher,
            protection_level=self.protection_level
        )

    @classmethod
    def _from_rest_object(cls, obj: RestIntellectualProperty) -> "IntellectualProperty":
        return IntellectualProperty(
            publisher=obj.publisher,
            protection_level=obj.protection_level
        )

    def _to_dict(self) -> Dict:
        return {
            "publisher": self.publisher,
            "protection_level": self.protection_level
        }

    def __eq__(self, other: Any) -> bool:
        return (
            self.publisher == other.publisher
            and self.protection_level == other.protection_level
        )
