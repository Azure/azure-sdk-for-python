# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental

module_logger = logging.getLogger(__name__)


@experimental
class DefaultDeploymentTemplateSchema(metaclass=PatchedSchemaMeta):
    """Schema for DefaultDeploymentTemplate."""

    asset_id = fields.Str(
        metadata={
            "description": "The asset ID of the deployment template. "
            "Format: azureml://registries/{registry_name}/deploymenttemplates/{template_name}/versions/{version}"
        }
    )

    @post_load
    def make(self, data, **kwargs):
        """Create DefaultDeploymentTemplate instance from loaded data.

        :param data: The deserialized data.
        :type data: dict
        :return: DefaultDeploymentTemplate instance.
        :rtype: ~azure.ai.ml.entities.DefaultDeploymentTemplate
        """
        from azure.ai.ml.entities._assets.default_deployment_template import DefaultDeploymentTemplate

        return DefaultDeploymentTemplate(**data)
