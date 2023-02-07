# TODO determine where this file should live.
from marshmallow import fields

from azure.ai.ml._schema.core.resource import YamlFileSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._schema.core.fields import DumpableStringField, NestedField, UnionField
from .data import DataSchema


# The YAML definition of a silo for describing a federated learning data target.
# Unlike most SDK/CLI schemas, this schema does not represent an AML resource;
# it is merely used to simplify the loading and validation of silos which are used
# to create FL pipeline nodes.
# Inherits from YamlFileSchema instead of something for specific because
# this does not represent a server-side resource.
@experimental
class FederatedLearningSiloSchema(YamlFileSchema):
    
    compute = fields.Str()
    datastore = fields.Str()
    # Todo - should this be a list or 1 single data
    # TODO: - is this overkill? What exact inputs do we need to pass to the backend to reference an existing 
    # data asset. Perhaps we shjould simplify this to an asset ID.
    inputs = UnionField([fields.List(NestedField(DataSchema)), NestedField(DataSchema)], is_strict=False)