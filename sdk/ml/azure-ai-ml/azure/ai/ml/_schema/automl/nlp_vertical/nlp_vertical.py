# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields

from azure.ai.ml._schema.automl.automl_vertical import AutoMLVerticalSchema
from azure.ai.ml._schema.automl.featurization_settings import NlpFeaturizationSettingsSchema
from azure.ai.ml._schema.automl.nlp_vertical.nlp_fixed_parameters import NlpFixedParametersSchema
from azure.ai.ml._schema.automl.nlp_vertical.nlp_parameter_subspace import NlpParameterSubspaceSchema
from azure.ai.ml._schema.automl.nlp_vertical.nlp_sweep_settings import NlpSweepSettingsSchema
from azure.ai.ml._schema.automl.nlp_vertical.nlp_vertical_limit_settings import NlpLimitsSchema
from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.job.input_output_entry import MLTableInputSchema
from azure.ai.ml.constants._job.automl import AutoMLConstants


class NlpVerticalSchema(AutoMLVerticalSchema):
    limits = NestedField(NlpLimitsSchema())
    sweep = NestedField(NlpSweepSettingsSchema())
    training_parameters = NestedField(NlpFixedParametersSchema())
    search_space = fields.List(NestedField(NlpParameterSubspaceSchema()))
    featurization = NestedField(NlpFeaturizationSettingsSchema(), data_key=AutoMLConstants.FEATURIZATION_YAML)
    validation_data = UnionField([NestedField(MLTableInputSchema)])
