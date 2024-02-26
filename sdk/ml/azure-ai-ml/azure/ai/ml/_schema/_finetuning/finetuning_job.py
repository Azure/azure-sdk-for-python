# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml._schema.job.input_output_fields_provider import OutputsField
from azure.ai.ml._utils._experimental import experimental

# This is meant to match the yaml definition NOT the models defined in _restclient


@experimental
class FineTuningJobSchema(BaseJobSchema):
    outputs = OutputsField()
