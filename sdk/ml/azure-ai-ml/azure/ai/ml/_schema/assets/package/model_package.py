# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.core.fields import VersionField, NestedField
from .inference_server import InferenceServerSchema
from .model_configuration import ModelConfigurationSchema
from .model_package_input import ModelPackageInputSchema
from .base_environment_source import BaseEnvironmentSourceSchema

module_logger = logging.getLogger(__name__)


class ModelPackageSchema(PathAwareSchema):
    target_environment_name = fields.Str(required=True, default="packaged-env")
    target_environment_version = VersionField()
    base_environment_source = NestedField(BaseEnvironmentSourceSchema)
    inferencing_server = NestedField(InferenceServerSchema)
    model_configuration = NestedField(ModelConfigurationSchema)
    inputs = fields.List(NestedField(ModelPackageInputSchema))
    tags = fields.Dict()
    environment_variables = fields.Dict(
        metadata={"description": "Environment variables configuration for the model package."}
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ModelPackage

        return ModelPackage(**data)
