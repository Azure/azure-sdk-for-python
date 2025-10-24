# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=trailing-whitespace,missing-final-newline

# pylint: disable=unused-argument

import logging

from marshmallow import fields, post_load

from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema, EnvironmentSchema
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    NestedField,
    PathAwareSchema,
    RegistryStr,
    UnionField,
    VersionField,
)
from azure.ai.ml._utils._experimental import experimental

from .probe_settings_schema import ProbeSettingsSchema
from .request_settings_schema import RequestSettingsSchema

module_logger = logging.getLogger(__name__)


@experimental
class DeploymentTemplateSchema(PathAwareSchema):
    name = fields.Str(required=True)
    description = fields.Str(metadata={"description": "Description of the deployment template ."})
    version = VersionField()
    tags = fields.Dict()
    type = fields.Str()
    deployment_template_type = fields.Str()
    environment_variables = fields.Dict(
        metadata={"description": "Environment variables configuration for the deployment."}
    )
    request_settings = NestedField(RequestSettingsSchema)
    liveness_probe = NestedField(ProbeSettingsSchema)
    readiness_probe = NestedField(ProbeSettingsSchema)
    instance_count = fields.Int()
    model_mount_path = fields.Str()
    allowed_instance_types = fields.Str()
    default_instance_type = fields.Str()
    environment = UnionField(
        [
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
            NestedField(EnvironmentSchema),
            NestedField(AnonymousEnvironmentSchema),
        ]
    )
    scoring_port = fields.Int()
    scoring_path = fields.Str()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        """Post-load processing to create DeploymentTemplate object from dictionary data.

        :param data: Dictionary of parsed values from the yaml.
        :type data: typing.Dict
        :return: DeploymentTemplate object made from the yaml
        :rtype: DeploymentTemplate
        """
        from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate

        # Handle field name mapping
        if "default_instance_type" in data and "instance_type" not in data:
            data["instance_type"] = data["default_instance_type"]

        # Remove the default_instance_type if both are present to avoid duplicate parameter
        if "default_instance_type" in data and "instance_type" in data:
            data.pop("default_instance_type")

        return DeploymentTemplate(**data)
