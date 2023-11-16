# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import post_load

from azure.ai.ml._schema.core.fields import ComputeField, EnvironmentField, StringTransformedEnum
from azure.ai.ml._schema.job import ParameterizedParallelSchema
from azure.ai.ml._schema.pipeline.component_job import BaseNodeSchema

from ...constants._component import NodeType

module_logger = logging.getLogger(__name__)


# parallel job inherits parallel attributes from ParameterizedParallelSchema and node functionality from BaseNodeSchema
class PipelineParallelJobSchema(BaseNodeSchema, ParameterizedParallelSchema):
    """Schema for ParallelJob in PipelineJob/PipelineComponent."""

    type = StringTransformedEnum(allowed_values=NodeType.PARALLEL)
    compute = ComputeField()
    environment = EnvironmentField()

    @post_load
    def make(self, data: Any, **kwargs: Any):
        """Construct a ParallelJob from deserialized data.

        :param data: The deserialized data.
        :type data: dict[str, Any]
        :return: A ParallelJob.
        :rtype: azure.ai.ml.entities._job.parallel.ParallelJob
        """
        from azure.ai.ml.entities._job.parallel.parallel_job import ParallelJob

        return ParallelJob(**data)
