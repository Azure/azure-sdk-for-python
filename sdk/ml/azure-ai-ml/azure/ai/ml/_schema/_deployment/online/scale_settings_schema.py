# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from azure.ai.ml._restclient.v2021_10_01.models import ScaleType
from azure.ai.ml._schema import PatchedSchemaMeta, StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from marshmallow import ValidationError, fields, post_load, validates_schema

module_logger = logging.getLogger(__name__)


class DefaultScaleSettingsSchema(metaclass=PatchedSchemaMeta):
    scale_type = StringTransformedEnum(
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
    scale_type = StringTransformedEnum(
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
