# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import ValidationError, fields, validates_schema

from azure.ai.ml._schema.core.fields import ArmStr, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants._common import LOCAL_COMPUTE_TARGET, AzureMLResourceType

module_logger = logging.getLogger(__name__)


class ComputeBindingSchema(metaclass=PatchedSchemaMeta):
    target = UnionField(
        [
            StringTransformedEnum(allowed_values=[LOCAL_COMPUTE_TARGET]),
            ArmStr(azureml_type=AzureMLResourceType.COMPUTE),
            # Case for virtual clusters
            ArmStr(azureml_type=AzureMLResourceType.VIRTUALCLUSTER),
        ]
    )
    instance_count = fields.Integer()
    instance_type = fields.Str(metadata={"description": "The instance type to make available to this job."})
    location = fields.Str(metadata={"description": "The locations where this job may run."})
    properties = fields.Dict(keys=fields.Str())

    @validates_schema
    def validate(self, data: Any, **kwargs):
        if data.get("target") == LOCAL_COMPUTE_TARGET and data.get("instance_count", 1) != 1:
            raise ValidationError("Local runs must have node count of 1.")
