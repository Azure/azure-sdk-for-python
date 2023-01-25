# TODO determine where this file should live.
from marshmallow import fields

from azure.ai.ml._schema.core.resource import ResourceSchema
from azure.ai.ml._utils._experimental import experimental


# The YAML definition of a silo for describing a federated learning data target.
# Unlike most SDK/CLI schemas, this schema does not represent an AML resource;
# it is merely used to simplify the loading and validation of silos which are used
# to create FL pipeline nodes.s
@experimental
class FederatedLearningSilo(ResourceSchema):
    
    # TODO determine remaining inputs
    location = fields.Str(required=True)