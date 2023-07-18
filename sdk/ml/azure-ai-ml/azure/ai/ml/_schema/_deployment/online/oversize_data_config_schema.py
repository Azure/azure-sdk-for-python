# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from marshmallow import ValidationError, fields, post_load, validates

from azure.ai.ml._schema import PatchedSchemaMeta
from azure.ai.ml._utils._storage_utils import AzureMLDatastorePathUri

module_logger = logging.getLogger(__name__)


class OversizeDataConfigSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str()

    # pylint: disable=unused-argument
    @validates("path")
    def validate_path(self, value, **kwargs):
        datastore_path = AzureMLDatastorePathUri(value)
        if datastore_path.uri_type != "Datastore":
            raise ValidationError(f"Path '{value}' is not a properly formatted datastore path.")

    # pylint: disable=unused-argument
    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.oversize_data_config import OversizeDataConfig

        return OversizeDataConfig(**data)
