# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,protected-access

from marshmallow import post_load, pre_dump

from azure.ai.ml._schema._sweep.sweep_fields_provider import EarlyTerminationField, SamplingAlgorithmField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class ImageSweepSettingsSchema(metaclass=PatchedSchemaMeta):
    sampling_algorithm = SamplingAlgorithmField()
    early_termination = EarlyTerminationField()

    @pre_dump
    def conversion(self, data, **kwargs):
        rest_obj = data._to_rest_object()
        rest_obj.early_termination = data.early_termination
        return rest_obj

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageSweepSettings

        return ImageSweepSettings(**data)
