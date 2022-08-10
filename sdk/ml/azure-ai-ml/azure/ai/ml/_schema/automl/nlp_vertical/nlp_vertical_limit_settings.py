# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class NlpLimitsSchema(metaclass=PatchedSchemaMeta):
    max_concurrent_trials = fields.Int()
    max_trials = fields.Int()
    timeout_minutes = fields.Int()  # type duration

    @post_load
    def make(self, data, **kwargs) -> "NlpLimitSettings":
        from azure.ai.ml.automl import NlpLimitSettings

        return NlpLimitSettings(**data)
