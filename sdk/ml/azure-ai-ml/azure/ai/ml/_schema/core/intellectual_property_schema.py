# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental


@experimental
class IntellectualPropertySchema(metaclass=PatchedSchemaMeta):

    publisher = fields.Str()
