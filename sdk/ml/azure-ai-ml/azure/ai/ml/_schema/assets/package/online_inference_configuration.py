# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from marshmallow import fields, post_load
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from .route import RouteSchema


module_logger = logging.getLogger(__name__)


class OnlineInferenceConfigurationSchema(PathAwareSchema):
    liveness_route = NestedField(RouteSchema)
    readiness_route = NestedField(RouteSchema)
    scoring_route = NestedField(RouteSchema)
    entry_script = fields.Str()
    configuration = fields.Dict()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts._package.inferencing_server import (
            OnlineInferenceConfiguration,
        )

        return OnlineInferenceConfiguration(**data)
