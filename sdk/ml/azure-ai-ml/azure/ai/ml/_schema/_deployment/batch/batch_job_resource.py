# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import  NestedField, PathAwareSchema
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._schema._deployment.batch.batch_job import BatchJobSchema
from azure.ai.ml._schema._deployment.batch.system_data_schema import SystemDataSchema

module_logger = logging.getLogger(__name__)


class BatchJobResourceSchema(PathAwareSchema):
    id = fields.Str(),
    name = fields.Str(),
    type = fields.Str(),
    properties = NestedField(BatchJobSchema),
    system_data = NestedField(SystemDataSchema)



    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._deployment.batch_job_resource import BatchJobResource

        return BatchJobResource(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
