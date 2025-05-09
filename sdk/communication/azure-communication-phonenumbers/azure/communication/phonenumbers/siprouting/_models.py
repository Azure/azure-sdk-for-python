# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class SipTrunk(object):
    """Represents a SIP trunk for routing calls. See RFC 4904.

    :ivar fqdn: FQDN of the trunk.
    :vartype fqdn: str
    :ivar sip_signaling_port: Gets or sets SIP signaling port of the trunk.
    :vartype sip_signaling_port: int
    :ivar enabled: Enabled flag.
    :vartype enabled: bool
    :ivar trunk_health: Represents health state of a SIP trunk for routing calls.
    :vartype trunk_health: ~azure.communication.phonenumbers.siprouting.models.TrunkHealth
    :ivar direct_transfer: When enabled, removes Azure Communication Services from the signaling
     path on call transfer and sets the SIP Refer-To header to the trunk's FQDN. By default false.
    :vartype direct_transfer: bool
    :ivar privacy_header: SIP Privacy header. Default value is id. Known values are: "id" and
     "none".
    :vartype privacy_header: str or
     ~azure.communication.phonenumbers.siprouting.models.PrivacyHeader
    :ivar ip_address_version: IP address version used by the trunk. Default value is ipv4. Known
     values are: "ipv4" and "ipv6".
    :vartype ip_address_version: str or
     ~azure.communication.phonenumbers.siprouting.models.IpAddressVersion
    """

    _attribute_map = {
        "fqdn": {"key": "fqdn", "type": "str"},
        "sip_signaling_port": {"key": "sipSignalingPort", "type": "int"},
        "enabled": {"key": "enabled", "type": "bool"},
        "trunk_health": {"key": "trunk_health", "type": "TrunkHealth"},
        "direct_transfer": {"key": "directTransfer", "type": "bool"},
        "privacy_header": {"key": "privacyHeader", "type": "str"},
        "ip_address_version": {"key": "ipAddressVersion", "type": "str"},
    }

    def __init__(self, **kwargs):
        """
        :keyword fqdn: FQDN of the trunk.
        :paramtype fqdn: str
        :keyword sip_signaling_port: Gets or sets SIP signaling port of the trunk.
        :paramtype sip_signaling_port: int
        :keyword enabled: Enabled flag.
        :paramtype enabled: bool
        :keyword trunk_health: Represents health state of a SIP trunk for routing calls.
        :paramtype trunk_health: ~azure.communication.phonenumbers.siprouting.models.TrunkHealth
        :keyword direct_transfer: When enabled, removes Azure Communication Services from the signaling
         path on call transfer and sets the SIP Refer-To header to the trunk's FQDN. By default false.
        :paramtype direct_transfer: bool
        :keyword privacy_header: SIP Privacy header. Default value is id. Known values are: "id" and
         "none".
        :keyword privacy_header: str or
         ~azure.communication.phonenumbers.siprouting.models.PrivacyHeader
        :keyword ip_address_version: IP address version used by the trunk. Default value is ipv4. Known
         values are: "ipv4" and "ipv6".
        :paramtype ip_address_version: str or
         ~azure.communication.phonenumbers.siprouting.models.IpAddressVersion
        """
        self.fqdn = kwargs.get("fqdn", None)
        self.sip_signaling_port = kwargs.get("sip_signaling_port", None)
        self.enabled = kwargs.get("enabled", None)
        self.trunk_health = kwargs.get("trunk_health", None)
        self.direct_transfer = kwargs.get("direct_transfer", None)
        self.privacy_header = kwargs.get("privacy_header", None)
        self.ip_address_version = kwargs.get("ip_address_version", None)

class SipTrunkRoute(object):
    """Represents a trunk route for routing calls.

    :ivar description: Gets or sets description of the route.
    :vartype description: str
    :ivar name: Gets or sets name of the route. Required.
    :vartype name: str
    :ivar number_pattern: Gets or sets regex number pattern for routing calls. .NET regex format is
     supported.
     The regex should match only digits with an optional '+' prefix without spaces.
     I.e. "^+[1-9][0-9]{3,23}$". Required.
    :vartype number_pattern: str
    :ivar trunks: Gets or sets list of SIP trunks for routing calls. Trunks are represented as
     FQDN.
    :vartype trunks: list[str]
    :ivar caller_id_override: Gets or sets caller ID override. This value will override caller ID
     of outgoing call specified at runtime.
    :vartype caller_id_override: str
    """

    _attribute_map = {
        "description": {"key": "description", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "number_pattern": {"key": "numberPattern", "type": "str"},
        "trunks": {"key": "trunks", "type": "[str]"},
        "caller_id_override": {"key": "callerIdOverride", "type": "str"},
    }

    def __init__(self, **kwargs):
        """
        :keyword description: Gets or sets description of the route.
        :paramtype description: Optional[str]
        :keyword name: Gets or sets name of the route. Required.
        :paramtype name: str
        :keyword number_pattern: Gets or sets regex number pattern for routing calls. .NET regex format
         is supported.
         The regex should match only digits with an optional '+' prefix without spaces.
         I.e. "^+[1-9][0-9]{3,23}$". Required.
        :paramtype number_pattern: str
        :keyword trunks: Gets or sets list of SIP trunks for routing calls. Trunks are represented as
         FQDN.
        :paramtype trunks: Optional[List[str]]
        :keyword caller_id_override: Gets or sets caller ID override. This value will override caller
         ID of outgoing call specified at runtime.
        :paramtype caller_id_override: str
        """
        self.description = kwargs.get("description", None)
        self.name = kwargs.get("name", None)
        self.number_pattern = kwargs.get("number_pattern", None)
        self.trunks = kwargs.get("trunks", None)
        self.caller_id_override = kwargs.get("caller_id_override", None)

class SipDomain(object):
    """Represents Domain object as response of validation api.
    Map key is domain.

    All required parameters must be populated in order to send to server.

    :ivar fqdn: FQDN of the trunk.
    :vartype fqdn: str
    :ivar enabled: Enabled flag. Required.
    :vartype enabled: bool
    """

    _attribute_map = {
        "fqdn": {"key": "fqdn", "type": "str"},
        "enabled": {"key": "enabled", "type": "bool"},
    }

    def __init__(self, **kwargs):
        """
        :keyword fqdn: FQDN of the trunk.
        :paramtype fqdn: str
        :keyword enabled: Enabled flag. Required.
        :paramtype enabled: bool
        """
        self.fqdn = kwargs.get("fqdn", None)
        self.enabled = kwargs.get("enabled", None)
        