# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging


from marshmallow import post_load
from .asset import AssetSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY

module_logger = logging.getLogger(__name__)


class ArtifactSchema(AssetSchema):
    @post_load
    def make(self, data, **kwargs):
        data[BASE_PATH_CONTEXT_KEY] = self.context[BASE_PATH_CONTEXT_KEY]
        return data
