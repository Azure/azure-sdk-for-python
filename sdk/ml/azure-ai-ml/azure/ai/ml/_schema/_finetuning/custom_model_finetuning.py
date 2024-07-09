# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Any, Dict
from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2024_01_01_preview.models import ModelProvider
from azure.ai.ml._schema._finetuning.finetuning_vertical import FineTuningVerticalSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._utils._experimental import experimental


@experimental
class CustomModelFineTuningSchema(FineTuningVerticalSchema):
    # This is meant to match the yaml definition NOT the models defined in _restclient

    model_provider = StringTransformedEnum(required=True, allowed_values=ModelProvider.CUSTOM)
    hyperparameters = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))

    @post_load
    def post_load_processing(self, data: Dict, **kwargs) -> Dict[str, Any]:
        """Post-load processing for the schema.

        :param data: Dictionary of parsed values from the yaml.
        :type data: typing.Dict

        :return Dictionary of parsed values from the yaml.
        :rtype Dict[str, Any]
        """

        data.pop("model_provider")
        return data
