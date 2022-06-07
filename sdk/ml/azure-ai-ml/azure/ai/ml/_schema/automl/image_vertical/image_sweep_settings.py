# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.automl.image_vertical.image_limit_settings import ImageSweepLimitSchema
from azure.ai.ml._schema._sweep.sweep_fields_provider import EarlyTerminationField, SamplingAlgorithmField
from marshmallow import post_load, pre_dump
from azure.ai.ml._schema import PatchedSchemaMeta, NestedField


class ImageSweepSettingsSchema(metaclass=PatchedSchemaMeta):
    limits = NestedField(ImageSweepLimitSchema())
    sampling_algorithm = SamplingAlgorithmField()
    early_termination = EarlyTerminationField()

    @pre_dump
    def conversion(self, data, **kwargs):
        return data._to_rest_object()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageSweepSettings

        limits = data.pop("limits")
        max_concurrent_trials = limits.max_concurrent_trials
        max_trials = limits.max_trials
        return ImageSweepSettings(max_concurrent_trials=max_concurrent_trials, max_trials=max_trials, **data)
