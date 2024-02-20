# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class RunSettingsSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str()
    display_name = fields.Str()
    experiment_name = fields.Str()
    description = fields.Str()
    tags = fields.Dict()
    settings = fields.Dict()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._deployment.run_settings import RunSettings

        return RunSettings(**data)
