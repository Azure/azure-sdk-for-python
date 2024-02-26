# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from azure.ai.ml._restclient.v2024_01_01_preview.models import ModelProvider
from azure.ai.ml._schema._finetuning.finetuning_vertical import FineTuningVerticalSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from marshmallow import fields
from typing import Any, Dict

from marshmallow import post_load

# This is meant to match the yaml definition NOT the models defined in _restclient


class CustomModelFineTuningSchema(FineTuningVerticalSchema):
    model_provider = StringTransformedEnum(required=True, allowed_values=ModelProvider.CUSTOM)
    hyperparameters = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))

    @post_load
    def make(self, data, **kwargs) -> Dict[str, Any]:
        data.pop("model_provider")

        return data
