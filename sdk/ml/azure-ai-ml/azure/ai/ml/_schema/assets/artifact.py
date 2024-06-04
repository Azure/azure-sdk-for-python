# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import fields, post_load

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

from .asset import AssetSchema

module_logger = logging.getLogger(__name__)


class ArtifactSchema(AssetSchema):
    datastore = fields.Str(metadata={"description": "Name of the datastore to upload to."}, required=False)

    @post_load
    def make(self, data, **kwargs):
        data[BASE_PATH_CONTEXT_KEY] = self.context[BASE_PATH_CONTEXT_KEY]
        return data
