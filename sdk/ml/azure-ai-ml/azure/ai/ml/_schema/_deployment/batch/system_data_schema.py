# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields

from azure.ai.ml._schema.core.fields import StringTransformedEnum, UnionField, PathAwareSchema
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._restclient.v2021_10_01.models import CreatedByType

module_logger = logging.getLogger(__name__)


class SystemDataSchema(PathAwareSchema):
    created_by = fields.Str()
    created_by_type = StringTransformedEnum(
        allowed_values=[CreatedByType.USER, CreatedByType.APPLICATION, CreatedByType.MANAGED_IDENTITY, CreatedByType.USER]
    )
    created_at = fields.DateTime()
    last_modified_by = fields.Str()
    last_modified_by_type = StringTransformedEnum(
        allowed_values=[CreatedByType.USER, CreatedByType.APPLICATION, CreatedByType.MANAGED_IDENTITY, CreatedByType.USER]
    )
    last_modified_at = fields.DateTime()

