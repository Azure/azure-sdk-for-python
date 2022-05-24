# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema import PatchedSchemaMeta
from azure.ai.ml._restclient.v2022_02_01_preview.models import ImageSweepLimitSettings


class ImageLimitsSchema(metaclass=PatchedSchemaMeta):
    max_concurrent_trials = fields.Int()
    max_trials = fields.Int()
    timeout_minutes = fields.Int()  # type duration

    @post_load
    def make(self, data, **kwargs):

        from azure.ai.ml.automl import ImageLimitSettings

        return ImageLimitSettings(**data)


class ImageSweepLimitSchema(metaclass=PatchedSchemaMeta):
    max_concurrent_trials = fields.Int()
    max_trials = fields.Int(data_key=AutoMLConstants.MAX_TRIALS_YAML)

    @post_load
    def make(self, data, **kwargs):
        return ImageSweepLimitSettings(**data)
