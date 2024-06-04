# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._restclient.v2022_02_01_preview.models import EarlyTerminationPolicyType
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake

module_logger = logging.getLogger(__name__)


class EarlyTerminationPolicySchema(metaclass=PatchedSchemaMeta):
    evaluation_interval = fields.Int(allow_none=True)
    delay_evaluation = fields.Int(allow_none=True)


class BanditPolicySchema(EarlyTerminationPolicySchema):
    type = StringTransformedEnum(
        required=True,
        allowed_values=EarlyTerminationPolicyType.BANDIT,
        casing_transform=camel_to_snake,
    )
    slack_factor = fields.Float(allow_none=True)
    slack_amount = fields.Float(allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import BanditPolicy

        data.pop("type", None)
        return BanditPolicy(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import BanditPolicy

        if not isinstance(data, BanditPolicy):
            raise ValidationError("Cannot dump non-BanditPolicy object into BanditPolicySchema")
        return data


class MedianStoppingPolicySchema(EarlyTerminationPolicySchema):
    type = StringTransformedEnum(
        required=True,
        allowed_values=EarlyTerminationPolicyType.MEDIAN_STOPPING,
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import MedianStoppingPolicy

        data.pop("type", None)
        return MedianStoppingPolicy(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import MedianStoppingPolicy

        if not isinstance(data, MedianStoppingPolicy):
            raise ValidationError("Cannot dump non-MedicanStoppingPolicy object into MedianStoppingPolicySchema")
        return data


class TruncationSelectionPolicySchema(EarlyTerminationPolicySchema):
    type = StringTransformedEnum(
        required=True,
        allowed_values=EarlyTerminationPolicyType.TRUNCATION_SELECTION,
        casing_transform=camel_to_snake,
    )
    truncation_percentage = fields.Int(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import TruncationSelectionPolicy

        data.pop("type", None)
        return TruncationSelectionPolicy(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import TruncationSelectionPolicy

        if not isinstance(data, TruncationSelectionPolicy):
            raise ValidationError(
                "Cannot dump non-TruncationSelectionPolicy object into TruncationSelectionPolicySchema"
            )
        return data
