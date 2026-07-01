# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Union

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

    def _to_rest_object(self) -> Dict[str, Any]:
        # ``AutoDeleteSetting`` was dropped from the arm_ml_service (2025-12) model; build the
        # 2023-04 wire body directly as a dict (JSON-direct).
        return {"condition": self.condition, "value": self.value}

    @classmethod
    def _from_rest_object(cls, obj: Any) -> "AutoDeleteSetting":
        # Accept both an arm hybrid / dict wire body and a legacy msrest object with attributes.
        condition = obj.get("condition") if hasattr(obj, "get") else obj.condition
        value = obj.get("value") if hasattr(obj, "get") else obj.value
        return cls(condition=condition, value=value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AutoDeleteSetting):
            return NotImplemented
        return self.condition == other.condition and self.value == other.value
