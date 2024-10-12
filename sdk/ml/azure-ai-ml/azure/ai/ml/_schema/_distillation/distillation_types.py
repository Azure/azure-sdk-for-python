# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental


@experimental
class DistillationPromptSettingsSchema(metaclass=PatchedSchemaMeta):
    enable_chain_of_thought = fields.Bool()
    enable_chain_of_density = fields.Bool()
    max_len_summary = fields.Number()
    # custom_prompt = fields.Str()
