# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PathAwareSchema
from .inference_server import InferenceServerSchema
from .model_configuration import ModelConfigurationSchema
from .model_package_input import ModelPackageInputSchema
from .base_environment_source import BaseEnvironmentSource
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._schema.core.fields import ArmVersionedStr, StringTransformedEnum, VersionField, NestedField

module_logger = logging.getLogger(__name__)


class ModelPackageSchema(PathAwareSchema):
    target_environment_name = fields.Str(required=True)
    target_environment_version = VersionField()
    base_environment_source = NestedField(BaseEnvironmentSource)
    inferencing_server = NestedField(InferenceServerSchema)
    model_configuration = NestedField(ModelConfigurationSchema)
    inputs = NestedField(ModelPackageInputSchema)
    tags = fields.Dict()
    environment_variables = fields.Dict(
        metadata={"description": "Environment variables configuration for the model package."}
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ModelPackage

        return ModelPackage(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
