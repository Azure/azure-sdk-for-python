# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from marshmallow import ValidationError, fields, post_load, validates

from azure.ai.ml._schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class SamplingStrategySchema(metaclass=PatchedSchemaMeta):
    sampling_rate = fields.Float()

    # pylint: disable=unused-argument,no-self-use
    @validates("sampling_rate")
    def validate_sampling_rate(self, value, **kwargs):
        if value >= 1.0 or value <= 0.0:
            raise ValidationError("Random Sample Percentage must be an number between 0.0-1.0")

    # pylint: disable=unused-argument,no-self-use
    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.sampling_strategy import SamplingStrategy

        return SamplingStrategy(**data)
