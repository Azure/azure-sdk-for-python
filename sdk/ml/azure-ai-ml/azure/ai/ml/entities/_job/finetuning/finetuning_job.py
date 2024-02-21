from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from typing import Any
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    FineTuningJob as RestFineTuningJob,
    UriFileJobInput,
)
from azure.ai.ml import Input
from azure.ai.ml.constants._common import AssetTypes


class FineTuningJob(Job, JobIOMixin):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        self.outputs = kwargs.pop("outputs", None)
        super().__init__(**kwargs)
