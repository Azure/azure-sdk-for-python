# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._restclient.v2024_01_01_preview.models import ModelProvider
from azure.ai.ml._schema._finetuning.azure_openai_hyperparameters import AzureOpenAiHyperparametersSchema
from azure.ai.ml._schema._finetuning.finetuning_vertical import FineTuningVerticalSchema

# This is meant to match the yaml definition NOT the models defined in _restclient


class AzureOpenAiFineTuningSchema(FineTuningVerticalSchema):
    model_provider = StringTransformedEnum(required=True, allowed_values=ModelProvider.AZURE_OPEN_AI)
    hyperparameters = AzureOpenAiHyperparametersSchema()
