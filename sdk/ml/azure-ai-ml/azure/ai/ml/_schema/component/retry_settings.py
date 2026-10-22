# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import DataBindingStr, UnionField


class RetrySettingsSchema(metaclass=PatchedSchemaMeta):
    timeout = UnionField([fields.Int(), DataBindingStr])
    max_retries = UnionField([fields.Int(), DataBindingStr])
