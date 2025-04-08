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
    """

    _attribute_map = {
        "fqdn": {"key": "fqdn", "type": "str"},
        "sip_signaling_port": {"key": "sipSignalingPort", "type": "int"},
    }

    def __init__(self, **kwargs):
        """
        :keyword fqdn: FQDN of the trunk.
        :paramtype fqdn: str
        :keyword sip_signaling_port: Gets or sets SIP signaling port of the trunk.
        :paramtype sip_signaling_port: int
        """
        self.fqdn = kwargs.get("fqdn", None)
        self.sip_signaling_port = kwargs.get("sip_signaling_port", None)


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
    """

    _attribute_map = {
        "description": {"key": "description", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "number_pattern": {"key": "numberPattern", "type": "str"},
        "trunks": {"key": "trunks", "type": "[str]"},
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
        """
        self.description = kwargs.get("description", None)
        self.name = kwargs.get("name", None)
        self.number_pattern = kwargs.get("number_pattern", None)
        self.trunks = kwargs.get("trunks", None)
