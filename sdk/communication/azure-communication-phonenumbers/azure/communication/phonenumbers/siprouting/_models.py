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
        'fqdn': {'key': 'fqdn', 'type': 'str'},
        'sip_signaling_port': {'key': 'sipSignalingPort', 'type': 'int'},
    }

    def __init__(
        self,
        **kwargs
    ):
        """
        :keyword fqdn: FQDN of the trunk.
        :paramtype fqdn: str
        :keyword sip_signaling_port: Gets or sets SIP signaling port of the trunk.
        :paramtype sip_signaling_port: int
        """
        self.fqdn = kwargs.get('fqdn', None)
        self.sip_signaling_port = kwargs.get('sip_signaling_port', None)
        