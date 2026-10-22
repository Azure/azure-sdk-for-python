# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument
from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class ScriptReferenceSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str()
    command = fields.Str()
    timeout_minutes = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._setup_scripts import ScriptReference

        return ScriptReference(**data)


class SetupScriptsSchema(metaclass=PatchedSchemaMeta):
    creation_script = NestedField(ScriptReferenceSchema())
    startup_script = NestedField(ScriptReferenceSchema())

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._setup_scripts import SetupScripts

        return SetupScripts(**data)
