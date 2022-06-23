# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from marshmallow import fields, post_load


class CommandJobLimitsSchema(metaclass=PatchedSchemaMeta):
    timeout = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import CommandJobLimits

        return CommandJobLimits(**data)


class SweepJobLimitsSchema(metaclass=PatchedSchemaMeta):
    max_concurrent_trials = fields.Int(metadata={"description": "Sweep Job max concurrent trials."})
    max_total_trials = fields.Int(
        metadata={"description": "Sweep Job max total trials."},
        required=True,
    )
    timeout = fields.Int(
        metadata={"description": "The max run duration in Seconds, after which the job will be cancelled."}
    )
    trial_timeout = fields.Int(metadata={"description": "Sweep Job Trial timeout value."})

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import SweepJobLimits

        return SweepJobLimits(**data)
