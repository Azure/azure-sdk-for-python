# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class QueueSettingsSchema(metaclass=PatchedSchemaMeta):
    job_tier = fields.Str(metadata={"description": "Dedicated/Spot."})

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import QueueSettings

        return QueueSettings(**data)