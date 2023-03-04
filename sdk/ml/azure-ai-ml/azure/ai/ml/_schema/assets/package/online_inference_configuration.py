# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema._deployment.deployment import DeploymentSchema
from azure.ai.ml._schema.core.fields import ExperimentalField, NestedField, StringTransformedEnum, UnionField
from .route import RouteSchema
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._restclient.v2023_04_01_preview.models import OnlineInferenceConfiguration


module_logger = logging.getLogger(__name__)


class OnlineInferenceConfigurationSchema(PathAwareSchema):
    liveness_route = NestedField(RouteSchema)
    readiness_route = NestedField(RouteSchema)
    scoring_route = NestedField(RouteSchema)
    entry_script = fields.Str()
    configuration = dict()

    @post_load
    def make(self, data, **kwargs):
        return OnlineInferenceConfiguration(**data)
