# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml.constants._job.finetuning import FineTuningConstants
from azure.ai.ml.constants._job import JobType
from azure.ai.ml._schema._finetuning.finetuning_job import FineTuningJobSchema

# This is meant to match the yaml definition NOT the models defined in _restclient


class AzureOpenAiFineTuningSchema(FineTuningJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=FineTuningConstants.AzureOpenAI)
    model_provider = StringTransformedEnum(required=True, allowed_values=JobType.FINE_TUNING)
