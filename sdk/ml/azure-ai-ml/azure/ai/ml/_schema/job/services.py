# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from marshmallow import fields, post_load
from ..core.schema import PathAwareSchema
from azure.ai.ml._restclient.v2021_10_01.models import JobService

module_logger = logging.getLogger(__name__)


class JobServiceSchema(PathAwareSchema):
    job_service_type = fields.Str()
    port = fields.Int()
    endpoint = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    error_message = fields.Str(dump_only=True)
    properties = fields.Dict()

    @post_load
    def make(self, data, **kwargs):
        return JobService(**data)
