# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Dict, Optional
from typing_extensions import Literal

from azure.ai.ml.constants._job.job import JobPriorityValues, JobTierNames
from azure.ai.ml._restclient.v2023_02_01_preview.models import QueueSettings as RestQueueSettings
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


@experimental
class QueueSettings(RestTranslatableMixin, DictMixin):
    """QueueSettings.
    :ivar job_tier: Enum to determine the job tier. Possible values include: "Spot", "Basic",
     "Standard", "Premium".
    :vartype job_tier: str or ~azure.mgmt.machinelearningservices.models.JobTier
    :ivar priority: Controls the priority of the job on a compute.
    :vartype priority: int
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
    def _from_rest_object(cls, obj: RestQueueSettings) -> "QueueSettings":
        if obj is None:
            return None
        job_tier = JobTierNames.REST_TO_ENTITY.get(obj.job_tier, None) if obj.job_tier else None
        priority = JobPriorityValues.REST_TO_ENTITY.get(obj.priority, None) if obj.priority else None
        return cls(job_tier=job_tier, priority=priority)

    def _validate(self):
        if self.job_tier and not self.job_tier in JobTierNames.ENTITY_TO_REST.keys():
            msg = f"job_tier should be one of " f"{JobTierNames.ALLOWED_NAMES}, but received '{self.job_tier}'."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        
        if self.priority and not self.priority in JobPriorityValues.ENTITY_TO_REST.keys():
            msg = f"priority should be one of " f"{JobPriorityValues.ALLOWED_VALUES}, but received '{self.priority}'."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )