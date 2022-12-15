# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from marshmallow import fields, post_load

from azure.ai.ml.entities._job.job_service import JobService

from ..core.schema import PathAwareSchema

module_logger = logging.getLogger(__name__)


class JobServiceSchema(PathAwareSchema):
    job_service_type = fields.Str()
    port = fields.Int()
    endpoint = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    nodes = fields.Str()
    error_message = fields.Str(dump_only=True)
    properties = fields.Dict()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return JobService(**data)
