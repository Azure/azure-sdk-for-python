# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import ValidationError, fields, post_load, validates_schema

from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml.entities._workspace.network_acls import DefaultActionType, IPRule, NetworkAcls


class IPRuleSchema(PathAwareSchema):
    """Schema for IPRule."""

    value = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        """Create an IPRule object from the marshmallow schema.

        :param data: The data from which the IPRule is being loaded.
        :type data: OrderedDict[str, Any]
        :returns: An IPRule object.
        :rtype: azure.ai.ml.entities._workspace.network_acls.NetworkAcls.IPRule
        """
        return IPRule(**data)


class NetworkAclsSchema(PathAwareSchema):
    """Schema for NetworkAcls.

    :param default_action: Specifies the default action when no IP rules are matched.
    :type default_action: str
    :param ip_rules: Rules governing the accessibility of a resource from a specific IP address or IP range.
    :type ip_rules: Optional[List[IPRule]]
    """

    default_action = fields.Str(required=True)
    ip_rules = fields.List(fields.Nested(IPRuleSchema), allow_none=True)

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        """Create a NetworkAcls object from the marshmallow schema.

        :param data: The data from which the NetworkAcls is being loaded.
        :type data: OrderedDict[str, Any]
        :returns: A NetworkAcls object.
        :rtype: azure.ai.ml.entities._workspace.network_acls.NetworkAcls
        """
        return NetworkAcls(**data)

    @validates_schema
    def validate_schema(self, data, **kwargs):  # pylint: disable=unused-argument
        """Validate the NetworkAcls schema.

        :param data: The data to validate.
        :type data: OrderedDict[str, Any]
        :raises ValidationError: If the schema is invalid.
        """
        if data["default_action"] not in set([DefaultActionType.DENY, DefaultActionType.ALLOW]):
            raise ValidationError("Invalid value for default_action. Must be 'Deny' or 'Allow'.")

        if data["default_action"] == DefaultActionType.DENY and not data.get("ip_rules"):
            raise ValidationError("ip_rules must be provided when default_action is 'Deny'.")
