# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_10_01.models import ScaleType
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake

module_logger = logging.getLogger(__name__)


class DefaultScaleSettingsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        required=True,
        allowed_values=ScaleType.DEFAULT,
        casing_transform=camel_to_snake,
        data_key="type",
    )

    @post_load
    def make(self, data: Any, **kwargs: Any) -> "DefaultScaleSettings":
        from azure.ai.ml.entities import DefaultScaleSettings

        return DefaultScaleSettings(**data)


class TargetUtilizationScaleSettingsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        required=True,
        allowed_values=ScaleType.TARGET_UTILIZATION,
        casing_transform=camel_to_snake,
        data_key="type",
    )
    polling_interval = fields.Int()
    target_utilization_percentage = fields.Int()
    min_instances = fields.Int()
    max_instances = fields.Int()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> "TargetUtilizationScaleSettings":
        from azure.ai.ml.entities import TargetUtilizationScaleSettings

        return TargetUtilizationScaleSettings(**data)
