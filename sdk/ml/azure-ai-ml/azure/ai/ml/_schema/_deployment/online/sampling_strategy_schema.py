# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from marshmallow import ValidationError, fields, post_load, validates

from azure.ai.ml._schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class SamplingStrategySchema(metaclass=PatchedSchemaMeta):
    random_sample_percentage = fields.Int()

    # pylint: disable=unused-argument,no-self-use
    @validates("random_sample_percentage")
    def validate_random_sample_percentage(self, value, **kwargs):
        if value > 100 or value < 1:
            raise ValidationError("Random Sample Percentage must be an integer from 1-100")

    # pylint: disable=unused-argument,no-self-use
    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.sampling_strategy import SamplingStrategy

        return SamplingStrategy(**data)
