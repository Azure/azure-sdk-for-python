# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import post_load

from azure.ai.ml._schema.job.import_job import ImportJobSchema

module_logger = logging.getLogger(__name__)


class PipelineImportJobSchema(ImportJobSchema):
    class Meta:
        exclude = ["compute"]  # compute property not applicable to import job

    @post_load
    def make(self, data: Any, **kwargs: Any):
        from azure.ai.ml.entities._job.import_job import ImportJob

        return ImportJob(**data)
