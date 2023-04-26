# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from marshmallow import fields, validate

from azure.ai.ml._restclient.v2022_02_01_preview.models import EndpointAuthMode
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.identity import IdentitySchema
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._endpoint import EndpointConfigurations

module_logger = logging.getLogger(__name__)


class EndpointSchema(PathAwareSchema):
    id = fields.Str()
    name = fields.Str(required=True, validate=validate.Regexp(EndpointConfigurations.NAME_REGEX_PATTERN))
    description = fields.Str(metadata={"description": "Description of the inference endpoint."})
    tags = fields.Dict()
    provisioning_state = fields.Str(metadata={"description": "Provisioning state for the endpoint."})
    properties = fields.Dict()
    auth_mode = StringTransformedEnum(
        allowed_values=[
            EndpointAuthMode.AML_TOKEN,
            EndpointAuthMode.KEY,
            EndpointAuthMode.AAD_TOKEN,
        ],
        casing_transform=camel_to_snake,
        metadata={
            "description": """authentication method: no auth, key based or azure ml token based.
            aad_token is only valid for batch endpoint."""
        },
    )
    scoring_uri = fields.Str(metadata={"description": "The endpoint uri that can be used for scoring"})
    location = fields.Str()
    openapi_uri = fields.Str(metadata={"description": "Endpoint Open API URI."})
    identity = NestedField(IdentitySchema)
