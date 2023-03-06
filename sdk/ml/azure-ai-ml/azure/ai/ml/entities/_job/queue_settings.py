# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import QueueSettings as RestQueueSettings
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin

module_logger = logging.getLogger(__name__)

class QueueSettings(RestTranslatableMixin, DictMixin):
    def __init__(self, *, job_tier: Optional[str] = None):
        self.job_tier = job_tier

    def _to_rest_object(self) -> RestQueueSettings:
        return RestQueueSettings(job_tier=self.job_tier)

    @classmethod
    def _from_rest_object(cls, obj: Optional[RestQueueSettings]) -> Optional["QueueSettings"]:
        if obj is None:
            return None
        return QueueSettings(job_tier=obj.job_tier,)