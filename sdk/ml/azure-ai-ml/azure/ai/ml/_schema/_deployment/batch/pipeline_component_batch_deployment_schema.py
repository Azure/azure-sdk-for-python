# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging
from typing import Any

from marshmallow import INCLUDE, fields, post_load

from azure.ai.ml._schema import (
    ArmVersionedStr,
    ArmStr,
    UnionField,
    RegistryStr,
    NestedField,
)
from azure.ai.ml._schema.core.fields import PipelineNodeNameStr, TypeSensitiveUnionField, PathAwareSchema
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineComponentFileRefField
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._component import NodeType

module_logger = logging.getLogger(__name__)


class PipelineComponentBatchDeploymentSchema(PathAwareSchema):
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
    type = fields.Str()
    job_definition = UnionField(
        [
            ArmStr(azureml_type=AzureMLResourceType.JOB),
            NestedField("PipelineSchema", unknown=INCLUDE),
        ]
    )
    tags = fields.Dict()
    description = fields.Str(metadata={"description": "Description of the endpoint deployment."})

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._deployment.pipeline_component_batch_deployment import (
            PipelineComponentBatchDeployment,
        )

        return PipelineComponentBatchDeployment(**data)


class NodeNameStr(PipelineNodeNameStr):
    def _get_field_name(self) -> str:
        return "Pipeline node"


def PipelineJobsField():
    pipeline_enable_job_type = {NodeType.PIPELINE: [NestedField("PipelineSchema", unknown=INCLUDE)]}

    pipeline_job_field = fields.Dict(
        keys=NodeNameStr(),
        values=TypeSensitiveUnionField(pipeline_enable_job_type),
    )

    return pipeline_job_field
