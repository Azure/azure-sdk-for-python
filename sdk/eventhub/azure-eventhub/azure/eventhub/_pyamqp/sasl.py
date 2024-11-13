# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._transport import SSLTransport, WebSocketTransport, AMQPS_PORT
from .constants import SASLCode, SASL_HEADER_FRAME, WEBSOCKET_PORT
from .performatives import SASLInit


_SASL_FRAME_TYPE = b"\x01"


class SASLPlainCredential(object):
    """PLAIN SASL authentication mechanism.
    See https://tools.ietf.org/html/rfc4616 for details
    """

    mechanism = b"PLAIN"

    def __init__(self, authcid, passwd, authzid=None):
        self.authcid = authcid
        self.passwd = passwd
        self.authzid = authzid

    def start(self):
        if self.authzid:
            login_response = self.authzid.encode("utf-8")
        else:
            login_response = b""
        login_response += b"\0"
        login_response += self.authcid.encode("utf-8")
        login_response += b"\0"
        login_response += self.passwd.encode("utf-8")
        return login_response


class SASLAnonymousCredential(object):
    """ANONYMOUS SASL authentication mechanism.
    See https://tools.ietf.org/html/rfc4505 for details
    """

    mechanism = b"ANONYMOUS"

    def start(self):
        return b""


class SASLExternalCredential(object):
    """EXTERNAL SASL mechanism.
    Enables external authentication, i.e. not handled through this protocol.
    Only passes 'EXTERNAL' as authentication mechanism, but no further
    authentication data.
    """

    mechanism = b"EXTERNAL"

    def start(self):
        return b""


class SASLTransportMixin:
    def _negotiate(self):
        self.write(SASL_HEADER_FRAME)
        _, returned_header = self.receive_frame()
        if returned_header[1] != SASL_HEADER_FRAME:
            raise ValueError(
                f"""Mismatching AMQP header protocol. Expected: {SASL_HEADER_FRAME!r},"""
                """received: {returned_header[1]!r}"""
            )

        _, supported_mechanisms = self.receive_frame(verify_frame_type=1)
        if self.credential.mechanism not in supported_mechanisms[1][0]:  # sasl_server_mechanisms
            raise ValueError("Unsupported SASL credential type: {}".format(self.credential.mechanism))
        sasl_init = SASLInit(
            mechanism=self.credential.mechanism,
            initial_response=self.credential.start(),
            hostname=self.host,
        )
        self.send_frame(0, sasl_init, frame_type=_SASL_FRAME_TYPE)

        _, next_frame = self.receive_frame(verify_frame_type=1)
        frame_type, fields = next_frame
        if frame_type != 0x00000044:  # SASLOutcome
            raise NotImplementedError("Unsupported SASL challenge")
        if fields[0] == SASLCode.Ok:  # code
            return
        raise ValueError("SASL negotiation failed.\nOutcome: {}\nDetails: {}".format(*fields))


class SASLTransport(SSLTransport, SASLTransportMixin):
    def __init__(
        self,
        host,
        credential,
        *,
        port=AMQPS_PORT,
        socket_timeout=None,
        ssl_opts=None,
        **kwargs,
    ):
        self.credential = credential
        ssl_opts = ssl_opts or True
        super(SASLTransport, self).__init__(
            host,
            port=port,
            socket_timeout=socket_timeout,
            ssl_opts=ssl_opts,
            **kwargs,
        )

    def negotiate(self):
        with self.block():
            self._negotiate()


class SASLWithWebSocket(WebSocketTransport, SASLTransportMixin):
    def __init__(
        self,
        host,
        credential,
        *,
        port=WEBSOCKET_PORT,
        socket_timeout=None,
        ssl_opts=None,
        **kwargs,
    ):
        self.credential = credential
        ssl_opts = ssl_opts or True
        super().__init__(
            host,
            port=port,
            socket_timeout=socket_timeout,
            ssl_opts=ssl_opts,
            **kwargs,
        )

    def negotiate(self):
        self._negotiate()
