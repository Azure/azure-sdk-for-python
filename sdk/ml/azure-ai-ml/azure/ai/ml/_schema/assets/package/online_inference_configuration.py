# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from marshmallow import fields, post_load
from azure.ai.ml._schema.core.fields import NestedField
from .route import RouteSchema
from azure.ai.ml._schema.core.schema import PathAwareSchema


module_logger = logging.getLogger(__name__)


class OnlineInferenceConfigurationSchema(PathAwareSchema):
    liveness_route = NestedField(RouteSchema)
    readiness_route = NestedField(RouteSchema)
    scoring_route = NestedField(RouteSchema)
    entry_script = fields.Str()
    configuration = dict()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts._package.custom_inferencing_server import (
            OnlineInferenceConfiguration,
        )

        return OnlineInferenceConfiguration(**data)
