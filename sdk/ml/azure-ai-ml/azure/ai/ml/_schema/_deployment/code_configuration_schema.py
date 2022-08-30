# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PathAwareSchema

module_logger = logging.getLogger(__name__)


class CodeConfigurationSchema(PathAwareSchema):
    code = fields.Str()
    scoring_script = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import CodeConfiguration

        return CodeConfiguration(**data)
