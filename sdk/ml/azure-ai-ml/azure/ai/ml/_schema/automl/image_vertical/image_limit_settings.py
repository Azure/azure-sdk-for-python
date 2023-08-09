# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class ImageLimitsSchema(metaclass=PatchedSchemaMeta):
    max_concurrent_trials = fields.Int()
    max_trials = fields.Int()
    timeout_minutes = fields.Int()  # type duration

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageLimitSettings

        return ImageLimitSettings(**data)
