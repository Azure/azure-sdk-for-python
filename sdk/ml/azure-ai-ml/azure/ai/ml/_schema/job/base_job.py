# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from marshmallow import fields

from azure.ai.ml._schema.core.fields import ArmStr, ComputeField, NestedField, UnionField
from azure.ai.ml._schema.core.resource import ResourceSchema
from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from azure.ai.ml.constants._common import AzureMLResourceType

from .creation_context import CreationContextSchema
from .services import (
    JobServiceSchema,
    SshJobServiceSchema,
    VsCodeJobServiceSchema,
    TensorBoardJobServiceSchema,
    JupyterLabJobServiceSchema,
)

module_logger = logging.getLogger(__name__)


class BaseJobSchema(ResourceSchema):
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    services = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(SshJobServiceSchema),
                NestedField(TensorBoardJobServiceSchema),
                NestedField(VsCodeJobServiceSchema),
                NestedField(JupyterLabJobServiceSchema),
                # JobServiceSchema should be the last in the list.
                # To support types not set by users like Custom, Tracking, Studio.
                NestedField(JobServiceSchema),
            ],
            is_strict=True,
        ),
    )
    name = fields.Str()
    id = ArmStr(azureml_type=AzureMLResourceType.JOB, dump_only=True, required=False)
    display_name = fields.Str(required=False)
    tags = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))
    status = fields.Str(dump_only=True)
    experiment_name = fields.Str()
    properties = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))
    description = fields.Str()
    log_files = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        dump_only=True,
        metadata={
            "description": (
                "The list of log files associated with this run. This section is only populated "
                "by the service and will be ignored if contained in a yaml sent to the service "
                "(e.g. via `az ml job create` ...)"
            )
        },
    )
    compute = ComputeField(required=False)
    identity = UnionField(
        [
            NestedField(ManagedIdentitySchema),
            NestedField(AMLTokenIdentitySchema),
            NestedField(UserIdentitySchema),
        ]
    )
