# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from marshmallow import ValidationError, fields, post_load, validates

from azure.ai.ml._schema import NestedField, PatchedSchemaMeta
from azure.ai.ml._schema._deployment.online.event_hub_schema import EventHubSchema
from azure.ai.ml._utils._storage_utils import AzureMLDatastorePathUri

module_logger = logging.getLogger(__name__)


class DestinationSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str()
    event_hub = NestedField(EventHubSchema)

    # pylint: disable=unused-argument,no-self-use
    @validates("path")
    def validate_path(self, value, **kwargs):
        datastore_path = AzureMLDatastorePathUri(value)
        if datastore_path.uri_type != "Datastore":
            raise ValidationError(f"Path '{value}' is not a properly formatted datastore path.")

    # pylint: disable=unused-argument,no-self-use
    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.destination import Destination

        return Destination(**data)
