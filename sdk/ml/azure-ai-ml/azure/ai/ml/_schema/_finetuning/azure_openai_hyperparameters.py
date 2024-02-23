# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class AzureOpenAiHyperparametersSchema(metaclass=PatchedSchemaMeta):
    n_epochs = fields.Int()
    learning_rate_multiplier = fields.Float()
    batch_size = fields.Int()
    # TODO: Should be dict<string,string>, check schema for the same.
    # For now not exposing as we dont have REST layer representation exposed.
    # Need to check with the team.
    # additional_parameters = fields.Dict()
