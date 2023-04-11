# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema import (
    ArmVersionedStr,
    PatchedSchemaMeta,
    StringTransformedEnum,
    UnionField,
    ArmStr,
    RegistryStr,
)
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineComponentFileRefField
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._job.job import JobType

module_logger = logging.getLogger(__name__)


class PipelineComponentBatchDeploymentSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str()
    endpoint_name = fields.Str()
    component = UnionField(
        [
            RegistryStr(azureml_type=AzureMLResourceType.COMPONENT),
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
            PipelineComponentFileRefField(),
        ]
    )
    settings = fields.Dict()
    name = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._deployment.pipeline_component_batch_deployment import PipelineComponentBatchDeployment

        return PipelineComponentBatchDeployment(**data)
