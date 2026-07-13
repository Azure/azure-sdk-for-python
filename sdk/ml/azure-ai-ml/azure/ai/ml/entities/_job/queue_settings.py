# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any, Dict, Optional, Union

from ..._restclient.arm_ml_service.models import QueueSettings as RestQueueSettings
from ..._utils._experimental import experimental
from ..._utils.utils import is_data_binding_expression
from ...constants._job.job import JobPriorityValues, JobTierNames
from ...entities._mixins import DictMixin, RestTranslatableMixin
from ...exceptions import (
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)

module_logger = logging.getLogger(__name__)


@experimental
class QueueSettings(RestTranslatableMixin, DictMixin):
    """Queue settings for a pipeline job.

    :ivar job_tier: Enum to determine the job tier. Possible values include: "Spot", "Basic",
        "Standard", "Premium", "Null".
    :vartype job_tier: str or ~azure.mgmt.machinelearningservices.models.JobTier
    :ivar priority: Controls the priority of the job on a compute.
    :vartype priority: str
    :keyword job_tier: The job tier. Accepted values are "Spot", "Basic", "Standard", and "Premium".
    :paramtype job_tier: Optional[Literal]]
    :keyword priority: The priority of the job on a compute. Accepted values are "low", "medium", and "high".
        Defaults to "medium".
    :paramtype priority: Optional[Literal]
    """

    def __init__(
        self,  # pylint: disable=unused-argument
        *,
        job_tier: Optional[str] = None,
        priority: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.job_tier = job_tier
        self.priority = priority

    def _to_rest_object(self) -> RestQueueSettings:
        self._validate()
        job_tier = JobTierNames.ENTITY_TO_REST.get(self.job_tier.lower(), None) if self.job_tier else None
        priority = JobPriorityValues.ENTITY_TO_REST.get(self.priority.lower(), None) if self.priority else None
        rest_obj = RestQueueSettings(job_tier=job_tier)
        # The shared arm_ml_service QueueSettings model dropped ``priority`` from its constructor; the legacy
        # msrest model carried it (as an int) on the wire, so preserve it as an unknown wire key.
        if priority is not None:
            rest_obj["priority"] = priority
        return rest_obj

    @classmethod
    def _from_rest_object(cls, obj: Union[Dict[str, Any], RestQueueSettings, None]) -> Optional["QueueSettings"]:
        if obj is None:
            return None
        if isinstance(obj, dict):
            queue_settings = RestQueueSettings._deserialize(obj, [])  # pylint: disable=protected-access
            return cls._from_rest_object(queue_settings)
        job_tier = JobTierNames.REST_TO_ENTITY.get(obj.job_tier, None) if obj.job_tier else None
        # ``priority`` is an unknown wire key on the arm hybrid (a MutableMapping); read it via mapping
        # access when present, else fall back to attribute access for legacy msrest objects.
        if getattr(obj, "_is_model", False) is True:
            rest_priority = obj.get("priority")
        else:
            rest_priority = obj.priority if hasattr(obj, "priority") else None
        priority = JobPriorityValues.REST_TO_ENTITY.get(rest_priority, None) if rest_priority else None
        return cls(job_tier=job_tier, priority=priority)

    def _validate(self) -> None:
        for key, enum_class in [
            ("job_tier", JobTierNames),
            ("priority", JobPriorityValues),
        ]:
            value = getattr(self, key)
            if is_data_binding_expression(value):
                msg = (
                    f"do not support data binding expression on {key} as it involves value mapping "
                    f"when transformed to rest object, but received '{value}'."
                )
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.JOB,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            valid_keys = list(enum_class.ENTITY_TO_REST.keys())  # type: ignore[attr-defined]
            if value and value.lower() not in valid_keys:
                msg = f"{key} should be one of {valid_keys}, but received '{value}'."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.JOB,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
