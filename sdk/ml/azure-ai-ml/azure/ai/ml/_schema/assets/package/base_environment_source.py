# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._restclient.v2023_04_01_preview.models import BaseEnvironmentId


module_logger = logging.getLogger(__name__)


class BaseEnvironmentSource(PathAwareSchema):
    type = fields.Str()
    resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return BaseEnvironmentId(**data)
