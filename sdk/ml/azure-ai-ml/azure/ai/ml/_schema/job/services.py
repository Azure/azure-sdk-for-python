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
    """This is to support tansformation of job services passed as dict type and
    internal job services like Custom, Tracking, Studio set by the system.
    """

    job_service_type = UnionField(
        [
            StringTransformedEnum(
                allowed_values=JobServiceTypeNames.NAMES_ALLOWED_FOR_PUBLIC,
                pass_original=True,
            ),
            fields.Str(),
        ]
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return JobService(**data)


class TensorBoardJobServiceSchema(JobServiceBaseSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                allowed_values="tensor_board",
                pass_original=True,
            )
        ]
    )
    log_dir = fields.Str()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return TensorBoardJobService(**data)


class SshJobServiceSchema(JobServiceBaseSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                # allowed_values=JobServiceTypeNames.NAMES_ALLOWED_FOR_PUBLIC,
                allowed_values="ssh",
                pass_original=True,
            )
        ]
    )
    ssh_public_keys = fields.Str()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return SshJobService(**data)


class VsCodeJobServiceSchema(JobServiceBaseSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                allowed_values="vs_code",
                pass_original=True,
            )
        ]
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return VsCodeJobService(**data)


class JupyterLabJobServiceSchema(JobServiceBaseSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                allowed_values="jupyter_lab",
                pass_original=True,
            )
        ]
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return JupyterLabJobService(**data)
