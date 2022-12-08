# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from marshmallow import fields, post_load

from azure.ai.ml.entities._job.job_service import JobService
from azure.ai.ml.constants._job.job import JobServiceTypeNames
from azure.ai.ml._schema.core.fields import StringTransformedEnum

from ..core.schema import PathAwareSchema

module_logger = logging.getLogger(__name__)

EntityNames = JobServiceTypeNames.EntityNames()


class JobServiceSchema(PathAwareSchema):
    job_service_type = StringTransformedEnum(
        allowed_values=[
            EntityNames.CUSTOM,
            EntityNames.TRACKING,
            EntityNames.STUDIO,
            EntityNames.JUPYTER_LAB,
            EntityNames.SSH,
            EntityNames.TENSOR_BOARD,
            EntityNames.VS_CODE,
        ],
    )
    port = fields.Int()
    endpoint = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    nodes = fields.Str()
    error_message = fields.Str(dump_only=True)
    properties = fields.Dict()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return JobService(**data)
