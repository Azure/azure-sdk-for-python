# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import AutoDeleteSetting as RestAutoDeleteSetting
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import AutoDeleteCondition
from azure.ai.ml.entities._mixins import DictMixin


@experimental
class AutoDeleteSetting(DictMixin):
    """Class which defines the auto delete setting.
    :param condition: When to check if an asset is expired.
     Possible values include: "CreatedGreaterThan", "LastAccessedGreaterThan".
    :type condition: AutoDeleteCondition
    :param value: Expiration condition value.
    :type value: str
    """

    def __init__(
        self,
        *,
        condition: AutoDeleteCondition = AutoDeleteCondition.CREATED_GREATER_THAN,
        value: Union[str, None] = None
    ):
        self.condition = condition
        self.value = value

    def _to_rest_object(self) -> RestAutoDeleteSetting:
        return RestAutoDeleteSetting(condition=self.condition, value=self.value)

    @classmethod
    def _from_rest_object(cls, obj: RestAutoDeleteSetting) -> "AutoDeleteSetting":
        return cls(condition=obj.condition, value=obj.value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AutoDeleteSetting):
            return NotImplemented
        return self.condition == other.condition and self.value == other.value
