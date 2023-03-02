# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema._deployment.deployment import DeploymentSchema
from azure.ai.ml._schema.core.fields import ExperimentalField, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PublicNetworkAccess
from .route import RouteSchema


module_logger = logging.getLogger(__name__)


class OnlineInferenceConfigurationSchema(DeploymentSchema):
    liveness_route = NestedField(RouteSchema)
    readiness_route = NestedField(RouteSchema)
    scoring_route = NestedField(RouteSchema)
    entry_script = fields.Str()
    configuration = dict()
