# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import ComputeField, NestedField, StringTransformedEnum
from azure.ai.ml._schema.job_resource_configuration import JobResourceConfigurationSchema
from azure.ai.ml._schema._deployment.deployment import DeploymentSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._deployment import BatchDeploymentType
from .model_batch_deployment_settings import ModelBatchDeploymentSettingsSchema


module_logger = logging.getLogger(__name__)


class ModelBatchDeploymentSchema(DeploymentSchema):
    compute = ComputeField(required=True)
    error_threshold = fields.Int(
        metadata={
            "description": """Error threshold, if the error count for the entire input goes above this value,\r\n
            the batch inference will be aborted. Range is [-1, int.MaxValue].\r\n
            For FileDataset, this value is the count of file failures.\r\n
            For TabularDataset, this value is the count of record failures.\r\n
            If set to -1 (the lower bound), all failures during batch inference will be ignored."""
        }
    )
    resources = NestedField(JobResourceConfigurationSchema)
    type = StringTransformedEnum(
        allowed_values=[BatchDeploymentType.PIPELINE, BatchDeploymentType.MODEL], required=False
    )

    settings = NestedField(ModelBatchDeploymentSettingsSchema)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import ModelBatchDeployment

        return ModelBatchDeployment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
