# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Any, Dict
from marshmallow import post_load


from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._restclient.v2024_01_01_preview.models import ModelProvider
from azure.ai.ml._schema._finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparametersSchema
from azure.ai.ml._schema._finetuning.finetuning_vertical import FineTuningVerticalSchema
from azure.ai.ml.entities._job.finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparameters
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml.constants._job.finetuning import FineTuningConstants
from azure.ai.ml._utils._experimental import experimental


@experimental
class AzureOpenAIFineTuningSchema(FineTuningVerticalSchema):
    # This is meant to match the yaml definition NOT the models defined in _restclient

    model_provider = StringTransformedEnum(
        required=True, allowed_values=ModelProvider.AZURE_OPEN_AI, casing_transform=camel_to_snake
    )
    hyperparameters = NestedField(AzureOpenAIHyperparametersSchema(), data_key=FineTuningConstants.HyperParameters)

    @post_load
    def post_load_processing(self, data: Dict, **kwargs) -> Dict[str, Any]:
        """Post load processing for the schema.

        :param data: Dictionary of parsed values from the yaml.
        :type data: typing.Dict

        :return Dictionary of parsed values from the yaml.
        :rtype Dict[str, Any]
        """
        data.pop("model_provider")
        hyperaparameters = data.pop("hyperparameters", None)

        if hyperaparameters and not isinstance(hyperaparameters, AzureOpenAIHyperparameters):
            hyperaparameters_dict = {}
            for key, value in hyperaparameters.items():
                hyperaparameters_dict[key] = value
            azure_openai_hyperparameters = AzureOpenAIHyperparameters(
                batch_size=hyperaparameters_dict.get("batch_size", None),
                learning_rate_multiplier=hyperaparameters_dict.get("learning_rate_multiplier", None),
                n_epochs=hyperaparameters_dict.get("n_epochs", None),
            )
            data["hyperparameters"] = azure_openai_hyperparameters
        return data
