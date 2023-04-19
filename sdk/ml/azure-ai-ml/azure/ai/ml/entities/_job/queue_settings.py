# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Any, Dict, Optional, Union

from typing_extensions import Literal

from ..._restclient.v2023_04_01_preview.models import QueueSettings as RestQueueSettings
from ..._utils._experimental import experimental
from ..._utils.utils import is_data_binding_expression
from ...constants._job.job import JobPriorityValues, JobTierNames
from ...entities._mixins import DictMixin, RestTranslatableMixin
from ...exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


@experimental
class QueueSettings(RestTranslatableMixin, DictMixin):
    """QueueSettings.
    :ivar job_tier: Enum to determine the job tier. Possible values include: "Spot", "Basic",
     "Standard", "Premium".
    :vartype job_tier: str or ~azure.mgmt.machinelearningservices.models.JobTier
    :ivar priority: Controls the priority of the job on a compute.
    :vartype priority: str
    """

    def __init__(
        self,
        *,
        job_tier: Optional[Literal["spot", "basic", "standard", "premium"]] = None,
        priority: Optional[Literal["low", "medium", "high"]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.job_tier = job_tier
        self.priority = priority

    def _to_rest_object(self) -> RestQueueSettings:
        self._validate()
        job_tier = JobTierNames.ENTITY_TO_REST.get(self.job_tier, None) if self.job_tier else None
        priority = JobPriorityValues.ENTITY_TO_REST.get(self.priority, None) if self.priority else None
        return RestQueueSettings(job_tier=job_tier, priority=priority)

    @classmethod
    def _from_rest_object(cls, obj: Union[Dict[str, Any], RestQueueSettings, None]) -> Optional["QueueSettings"]:
        if obj is None:
            return None
        if isinstance(obj, dict):
            queue_settings = RestQueueSettings.from_dict(obj)
            return cls._from_rest_object(queue_settings)
        job_tier = JobTierNames.REST_TO_ENTITY.get(obj.job_tier, None) if obj.job_tier else None
        priority = JobPriorityValues.REST_TO_ENTITY.get(obj.priority, None) if obj.priority else None
        return cls(job_tier=job_tier, priority=priority)

    def _validate(self):
        for key, enum_class in [("job_tier", JobTierNames), ("priority", JobPriorityValues)]:
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
            valid_keys = list(enum_class.ENTITY_TO_REST.keys())
            if value and value not in valid_keys:
                msg = f"{key} should be one of {valid_keys}, but received '{value}'."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.JOB,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
