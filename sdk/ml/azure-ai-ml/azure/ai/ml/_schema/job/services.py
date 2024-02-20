# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from marshmallow import fields, post_load

from azure.ai.ml.entities._job.job_service import (
    JobService,
    SshJobService,
    JupyterLabJobService,
    VsCodeJobService,
    TensorBoardJobService,
)
from azure.ai.ml.constants._job.job import JobServiceTypeNames
from azure.ai.ml._schema.core.fields import StringTransformedEnum, UnionField

from ..core.schema import PathAwareSchema

module_logger = logging.getLogger(__name__)


class JobServiceBaseSchema(PathAwareSchema):
    port = fields.Int()
    endpoint = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    nodes = fields.Str()
    error_message = fields.Str(dump_only=True)
    properties = fields.Dict()


class JobServiceSchema(JobServiceBaseSchema):
    """This is to support tansformation of job services passed as dict type and internal job services like Custom,
    Tracking, Studio set by the system."""

    type = UnionField(
        [
            StringTransformedEnum(
                allowed_values=JobServiceTypeNames.NAMES_ALLOWED_FOR_PUBLIC,
                pass_original=True,
            ),
            fields.Str(),
        ]
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        data.pop("type", None)
        return JobService(**data)


class TensorBoardJobServiceSchema(JobServiceBaseSchema):
    type = StringTransformedEnum(
        allowed_values=JobServiceTypeNames.EntityNames.TENSOR_BOARD,
        pass_original=True,
    )
    log_dir = fields.Str()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        data.pop("type", None)
        return TensorBoardJobService(**data)


class SshJobServiceSchema(JobServiceBaseSchema):
    type = StringTransformedEnum(
        allowed_values=JobServiceTypeNames.EntityNames.SSH,
        pass_original=True,
    )
    ssh_public_keys = fields.Str()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        data.pop("type", None)
        return SshJobService(**data)


class VsCodeJobServiceSchema(JobServiceBaseSchema):
    type = StringTransformedEnum(
        allowed_values=JobServiceTypeNames.EntityNames.VS_CODE,
        pass_original=True,
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        data.pop("type", None)
        return VsCodeJobService(**data)


class JupyterLabJobServiceSchema(JobServiceBaseSchema):
    type = StringTransformedEnum(
        allowed_values=JobServiceTypeNames.EntityNames.JUPYTER_LAB,
        pass_original=True,
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        data.pop("type", None)
        return JupyterLabJobService(**data)
