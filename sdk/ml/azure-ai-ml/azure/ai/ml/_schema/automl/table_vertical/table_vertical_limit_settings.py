# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema import PatchedSchemaMeta


class AutoMLTableLimitsSchema(metaclass=PatchedSchemaMeta):
    enable_early_termination = fields.Bool()
    exit_score = fields.Float()
    max_concurrent_trials = fields.Int()
    max_cores_per_trial = fields.Int()
    max_trials = fields.Int(data_key=AutoMLConstants.MAX_TRIALS_YAML)
    timeout_minutes = fields.Int()  # type duration
    trial_timeout_minutes = fields.Int()  # type duration

    @post_load
    def make(self, data, **kwargs) -> "TabularLimitSettings":
        from azure.ai.ml.automl import TabularLimitSettings

        return TabularLimitSettings(**data)
