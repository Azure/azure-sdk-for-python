# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from marshmallow import fields, post_load

from azure.ai.ml.entities._job.job_service import JobService, SshJobService, JupyterLabJobService, VsCodeJobService, TensorBoardJobService
from azure.ai.ml.constants._job.job import JobServiceTypeNames
from azure.ai.ml._schema.core.fields import StringTransformedEnum, UnionField

from ..core.schema import PathAwareSchema

module_logger = logging.getLogger(__name__)

# TODO: Can JobServiceSchema removed?
class JobServiceSchema(PathAwareSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                allowed_values=JobServiceTypeNames.NAMES_ALLOWED_FOR_PUBLIC,
                pass_original=True,
            )
        ]
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


# **********TODO: Refactor: Create base class or util functions
class TensorBoardJobServiceSchema(PathAwareSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                allowed_values="tensor_board",
                pass_original=True,
            )
            # ,
            # fields.Str(),
        ]
    )
    port = fields.Int()
    endpoint = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    nodes = fields.Str()
    log_dir = fields.Str()
    error_message = fields.Str(dump_only=True)
    properties = fields.Dict()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return TensorBoardJobService(**data)

# **********TODO: Refactor: Create base class or util functions
class SshJobServiceSchema(PathAwareSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                # allowed_values=JobServiceTypeNames.NAMES_ALLOWED_FOR_PUBLIC,
                allowed_values="ssh",
                pass_original=True,
            )
            # ,
            # fields.Str(),
        ]
    )
    port = fields.Int()
    endpoint = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    nodes = fields.Str()
    ssh_public_keys = fields.Str()
    error_message = fields.Str(dump_only=True)
    properties = fields.Dict()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return SshJobService(**data)

# **********TODO: Refactor: Create base class or util functions
class VsCodeJobServiceSchema(PathAwareSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                allowed_values="vs_code",
                pass_original=True,
            )
            # ,
            # fields.Str(),
        ]
    )
    port = fields.Int()
    endpoint = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    nodes = fields.Str()
    error_message = fields.Str(dump_only=True)
    properties = fields.Dict()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return VsCodeJobService(**data)


# **********TODO: Refactor: Create base class or util functions
class JupyterLabJobServiceSchema(PathAwareSchema):
    job_service_type = UnionField(
        [
            StringTransformedEnum(
                allowed_values="jupyter_lab",
                pass_original=True,
            )
            # ,
            # fields.Str(),
        ]
    )
    port = fields.Int()
    endpoint = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    nodes = fields.Str()
    error_message = fields.Str(dump_only=True)
    properties = fields.Dict()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return JupyterLabJobService(**data)
