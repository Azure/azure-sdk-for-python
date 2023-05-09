# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# # TODO determine where this file should live.
from marshmallow import fields

from azure.ai.ml._schema.core.resource import YamlFileSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField


# Inherits from YamlFileSchema instead of something for specific because
# this does not represent a server-side resource.
@experimental
class FederatedLearningSiloSchema(YamlFileSchema):
    """The YAML definition of a silo for describing a federated learning data target.
    Unlike most SDK/CLI schemas, this schema does not represent an AML resource;
    it is merely used to simplify the loading and validation of silos which are used
    to create FL pipeline nodes.
    """

    compute = fields.Str()
    datastore = fields.Str()
    inputs = InputsField()
