from marshmallow import fields, post_load
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental

@experimental
class IntellectualPropertySchema(metaclass=PatchedSchemaMeta):

    publisher = fields.Str()
