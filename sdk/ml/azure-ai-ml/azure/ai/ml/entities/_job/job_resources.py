# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, List
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2024_10_01_preview.models import JobResources as RestJobResources


class JobResources(RestTranslatableMixin):
    """Resource configuration for a job.

    This class should not be instantiated directly. Instead, use its subclasses.
    """

    def __init__(self, *, instance_types: List[str]) -> None:
        self.instance_types = instance_types

    def _to_rest_object(self) -> Any:
        return RestJobResources(instance_types=self.instance_types)

    @classmethod
    def _from_rest_object(cls, obj: RestJobResources) -> "JobResources":
        job_resources = cls(instance_types=obj.instance_types)
        return job_resources

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JobResources):
            return NotImplemented
        return self.instance_types == other.instance_types

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
