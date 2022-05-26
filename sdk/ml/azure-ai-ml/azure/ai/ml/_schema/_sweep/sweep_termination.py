# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    EarlyTerminationPolicyType,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import StringTransformedEnum

module_logger = logging.getLogger(__name__)


class EarlyTerminationPolicySchema(metaclass=PatchedSchemaMeta):
    evaluation_interval = fields.Int()
    delay_evaluation = fields.Int()


class BanditPolicySchema(EarlyTerminationPolicySchema):
    type = StringTransformedEnum(
        required=True, allowed_values=EarlyTerminationPolicyType.BANDIT, casing_transform=camel_to_snake
    )
    slack_factor = fields.Float()
    slack_amount = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import BanditPolicy

        return BanditPolicy(**data)


class MedianStoppingPolicySchema(EarlyTerminationPolicySchema):
    type = StringTransformedEnum(
        required=True, allowed_values=EarlyTerminationPolicyType.MEDIAN_STOPPING, casing_transform=camel_to_snake
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import MedianStoppingPolicy

        return MedianStoppingPolicy(**data)


class TruncationSelectionPolicySchema(EarlyTerminationPolicySchema):
    type = StringTransformedEnum(
        required=True, allowed_values=EarlyTerminationPolicyType.TRUNCATION_SELECTION, casing_transform=camel_to_snake
    )
    truncation_percentage = fields.Int(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import TruncationSelectionPolicy

        return TruncationSelectionPolicy(**data)
