# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema.automl.automl_vertical import AutoMLVerticalSchema
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.automl.featurization_settings import NlpFeaturizationSettingsSchema
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField
from azure.ai.ml._schema.automl.nlp_vertical.nlp_vertical_limit_settings import NlpLimitsSchema


class NlpVerticalSchema(AutoMLVerticalSchema):
    limits = NestedField(NlpLimitsSchema())
    featurization = NestedField(NlpFeaturizationSettingsSchema(), data_key=AutoMLConstants.FEATURIZATION_YAML)
    validation_data = InputsField()
