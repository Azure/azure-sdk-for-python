# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class RetrySettingsSchema(metaclass=PatchedSchemaMeta):
    timeout = fields.Int()
    max_retries = fields.Int()
