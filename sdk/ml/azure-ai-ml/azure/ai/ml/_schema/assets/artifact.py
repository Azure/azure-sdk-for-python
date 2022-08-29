# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import post_load, fields

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY

from .asset import AssetSchema

module_logger = logging.getLogger(__name__)


class ArtifactSchema(AssetSchema):
    datastore = fields.Str(metadata={"description": "Name of the datastore to upload to."}, required=False)

    @post_load
    def make(self, data, **kwargs):
        data[BASE_PATH_CONTEXT_KEY] = self.context[BASE_PATH_CONTEXT_KEY]
        return data
