# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import TYPE
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin


@experimental
class SyntheticDataGenerationJob(Job, JobIOMixin):
    def __init__(self, **kwargs: Any) -> None:
        kwargs[TYPE] = JobType.DATA_GENERATION
        self.outputs = kwargs.pop("outputs", None)
        super().__init__(**kwargs)
