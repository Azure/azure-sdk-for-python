# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import PathAwareSchema

module_logger = logging.getLogger(__name__)


class BatchDeploymentBaseModelSchema(PathAwareSchema):
    name = fields.Str()
    endpoint_name = fields.Str()
    name = fields.Str()
    type = fields.Str()
    tags = fields.Dict()
    description = fields.Str(metadata={"description": "Description of the endpoint deployment."})

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._deployment.batch_deployment_base_model import (
            BatchDeploymentBaseModel,
        )

        return BatchDeploymentBaseModel(**data)


