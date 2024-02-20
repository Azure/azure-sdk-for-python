# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields


class AzureOpenAiHyperparametersSchema:
    n_epochs = fields.Int()
    learning_rate_multiplier = fields.Float()
    batch_size = fields.Int()
    # TODO: Should be dict<string,string>, check schema for the same.
    additional_parameters = fields.Dict()
