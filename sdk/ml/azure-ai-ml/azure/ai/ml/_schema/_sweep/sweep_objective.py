# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._restclient.v2021_10_01.models import (
    Goal,
)
from azure.ai.ml._utils.utils import camel_to_snake

module_logger = logging.getLogger(__name__)


class SweepObjectiveSchema(metaclass=PatchedSchemaMeta):
    goal = StringTransformedEnum(
        required=True, allowed_values=[Goal.MINIMIZE, Goal.MAXIMIZE], casing_transform=camel_to_snake
    )
    primary_metric = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs) -> "Objective":
        from azure.ai.ml.entities._job.sweep.objective import Objective

        return Objective(**data)
