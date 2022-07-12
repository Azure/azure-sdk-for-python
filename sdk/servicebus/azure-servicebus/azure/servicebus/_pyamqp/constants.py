#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from enum import Enum
import struct

_AS_BYTES = struct.Struct('>B')

#: The IANA assigned port number for AMQP.The standard AMQP port number that has been assigned by IANA
#: for TCP, UDP, and SCTP.There are currently no UDP or SCTP mappings defined for AMQP.
#: The port number is reserved for future transport mappings to these protocols.
PORT = 5672

# default port for AMQP over Websocket
WEBSOCKET_PORT = 443

# subprotocol for AMQP over Websocket
AMQP_WS_SUBPROTOCOL = 'AMQPWSB10'

#: The IANA assigned port number for secure AMQP (amqps).The standard AMQP port number that has been assigned
#: by IANA for secure TCP using TLS. Implementations listening on this port should NOT expect a protocol
#: handshake before TLS is negotiated.
SECURE_PORT = 5671


# default port for AMQP over Websocket
WEBSOCKET_PORT = 443


# subprotocol for AMQP over Websocket
AMQP_WS_SUBPROTOCOL = 'AMQPWSB10'


MAJOR = 1  #: Major protocol version.
MINOR = 0  #: Minor protocol version.
REV = 0  #: Protocol revision.
HEADER_FRAME = b"AMQP\x00" + _AS_BYTES.pack(MAJOR) + _AS_BYTES.pack(MINOR) + _AS_BYTES.pack(REV)


TLS_MAJOR = 1  #: Major protocol version.
TLS_MINOR = 0  #: Minor protocol version.
TLS_REV = 0  #: Protocol revision.
TLS_HEADER_FRAME = b"AMQP\x02" + _AS_BYTES.pack(TLS_MAJOR) + _AS_BYTES.pack(TLS_MINOR) + _AS_BYTES.pack(TLS_REV)

SASL_MAJOR = 1  #: Major protocol version.
SASL_MINOR = 0  #: Minor protocol version.
SASL_REV = 0  #: Protocol revision.
SASL_HEADER_FRAME = b"AMQP\x03" + _AS_BYTES.pack(SASL_MAJOR) + _AS_BYTES.pack(SASL_MINOR) + _AS_BYTES.pack(SASL_REV)

EMPTY_FRAME = b'\x00\x00\x00\x08\x02\x00\x00\x00'

#: The lower bound for the agreed maximum frame size (in bytes). During the initial Connection negotiation, the
#: two peers must agree upon a maximum frame size. This constant defines the minimum value to which the maximum
#: frame size can be set. By defining this value, the peers can guarantee that they can send frames of up to this
#: size until they have agreed a definitive maximum frame size for that Connection.
MIN_MAX_FRAME_SIZE = 512
MAX_FRAME_SIZE_BYTES = 1024 * 1024
MAX_CHANNELS = 65535
INCOMING_WINDOW = 64 * 1024
OUTGOING_WIDNOW = 64 * 1024

DEFAULT_LINK_CREDIT = 10000

STRING_FILTER = b"apache.org:selector-filter:string"

DEFAULT_AUTH_TIMEOUT = 60
AUTH_DEFAULT_EXPIRATION_SECONDS = 3600
TOKEN_TYPE_JWT = "jwt"
TOKEN_TYPE_SASTOKEN = "servicebus.windows.net:sastoken"
CBS_PUT_TOKEN = "put-token"
CBS_NAME = "name"
CBS_OPERATION = "operation"
CBS_TYPE = "type"
CBS_EXPIRATION = "expiration"

SEND_DISPOSITION_ACCEPT = "accepted"
SEND_DISPOSITION_REJECT = "rejected"

AUTH_TYPE_SASL_PLAIN = "AUTH_SASL_PLAIN"
AUTH_TYPE_CBS = "AUTH_CBS"


class ConnectionState(Enum):
    #: In this state a Connection exists, but nothing has been sent or received. This is the state an
    #: implementation would be in immediately after performing a socket connect or socket accept.
    START = 0
    #: In this state the Connection header has been received from our peer, but we have not yet sent anything.
    HDR_RCVD = 1
    #: In this state the Connection header has been sent to our peer, but we have not yet received anything.
    HDR_SENT = 2
    #: In this state we have sent and received the Connection header, but we have not yet sent or
    #: received an open frame.
    HDR_EXCH = 3
    #: In this state we have sent both the Connection header and the open frame, but
    #: we have not yet received anything.
    OPEN_PIPE = 4
    #: In this state we have sent the Connection header, the open frame, any pipelined Connection traffic,
    #: and the close frame, but we have not yet received anything.
    OC_PIPE = 5
    #: In this state we have sent and received the Connection header, and received an open frame from
    #: our peer, but have not yet sent an open frame.
    OPEN_RCVD = 6
    #: In this state we have sent and received the Connection header, and sent an open frame to our peer,
    #: but have not yet received an open frame.
    OPEN_SENT = 7
    #: In this state we have send and received the Connection header, sent an open frame, any pipelined
    #: Connection traffic, and the close frame, but we have not yet received an open frame.
    CLOSE_PIPE = 8
    #: In this state the Connection header and the open frame have both been sent and received.
    OPENED = 9
    #: In this state we have received a close frame indicating that our partner has initiated a close.
    #: This means we will never have to read anything more from this Connection, however we can
    #: continue to write frames onto the Connection. If desired, an implementation could do a TCP half-close
    #: at this point to shutdown the read side of the Connection.
    CLOSE_RCVD = 10
    #: In this state we have sent a close frame to our partner. It is illegal to write anything more onto
    #: the Connection, however there may still be incoming frames. If desired, an implementation could do
    #: a TCP half-close at this point to shutdown the write side of the Connection.
    CLOSE_SENT = 11
    #: The DISCARDING state is a variant of the CLOSE_SENT state where the close is triggered by an error.
    #: In this case any incoming frames on the connection MUST be silently discarded until the peer's close
    #: frame is received.
    DISCARDING = 12
    #: In this state it is illegal for either endpoint to write anything more onto the Connection. The
    #: Connection may be safely closed and discarded.
    END = 13


class SessionState(Enum):
    #: In the UNMAPPED state, the Session endpoint is not mapped to any incoming or outgoing channels on the
    #: Connection endpoint. In this state an endpoint cannot send or receive frames.
    UNMAPPED = 0
    #: In the BEGIN_SENT state, the Session endpoint is assigned an outgoing channel number, but there is no entry
    #: in the incoming channel map. In this state the endpoint may send frames but cannot receive them.
    BEGIN_SENT = 1
    #: In the BEGIN_RCVD state, the Session endpoint has an entry in the incoming channel map, but has not yet
    #: been assigned an outgoing channel number. The endpoint may receive frames, but cannot send them.
    BEGIN_RCVD = 2
    #: In the MAPPED state, the Session endpoint has both an outgoing channel number and an entry in the incoming
    #: channel map. The endpoint may both send and receive frames.
    MAPPED = 3
    #: In the END_SENT state, the Session endpoint has an entry in the incoming channel map, but is no longer
    #: assigned an outgoing channel number. The endpoint may receive frames, but cannot send them.
    END_SENT = 4
    #: In the END_RCVD state, the Session endpoint is assigned an outgoing channel number, but there is no entry in
    #: the incoming channel map. The endpoint may send frames, but cannot receive them.
    END_RCVD = 5
    #: The DISCARDING state is a variant of the END_SENT state where the end is triggered by an error. In this
    #: case any incoming frames on the session MUST be silently discarded until the peer's end frame is received.
    DISCARDING = 6


class SessionTransferState(Enum):

    OKAY = 0
    ERROR = 1
    BUSY = 2


class LinkDeliverySettleReason(Enum):

    DISPOSITION_RECEIVED = 0
    SETTLED = 1
    NOT_DELIVERED = 2
    TIMEOUT = 3
    CANCELLED = 4


class LinkState(Enum):

    DETACHED = 0
    ATTACH_SENT = 1
    ATTACH_RCVD = 2
    ATTACHED = 3
    DETACH_SENT = 4
    DETACH_RCVD = 5
    ERROR = 6


class ManagementLinkState(Enum):

    IDLE = 0
    OPENING = 1
    CLOSING = 2
    OPEN = 3
    ERROR = 4


class ManagementOpenResult(Enum):

    OPENING = 0
    OK = 1
    ERROR = 2
    CANCELLED = 3


class ManagementExecuteOperationResult(Enum):

    OK = 0
    ERROR = 1
    FAILED_BAD_STATUS = 2
    LINK_CLOSED = 3


class CbsState(Enum):
    CLOSED = 0
    OPENING = 1
    OPEN = 2
    ERROR = 3


class CbsAuthState(Enum):
    OK = 0
    IDLE = 1
    IN_PROGRESS = 2
    TIMEOUT = 3
    REFRESH_REQUIRED = 4
    EXPIRED = 5
    ERROR = 6  # Put token rejected or complete but fail authentication
    FAILURE = 7  # Fail to open cbs links


class Role(object):
    """Link endpoint role.

    Valid Values:
        - False: Sender
        - True: Receiver

    <type name="role" class="restricted" source="boolean">
        <choice name="sender" value="false"/>
        <choice name="receiver" value="true"/>
    </type>
    """
    Sender = False
    Receiver = True


class SenderSettleMode(object):
    """Settlement policy for a Sender.

    Valid Values:
        - 0: The Sender will send all deliveries initially unsettled to the Receiver.
        - 1: The Sender will send all deliveries settled to the Receiver.
        - 2: The Sender may send a mixture of settled and unsettled deliveries to the Receiver.

    <type name="sender-settle-mode" class="restricted" source="ubyte">
        <choice name="unsettled" value="0"/>
        <choice name="settled" value="1"/>
        <choice name="mixed" value="2"/>
    </type>
    """
    Unsettled = 0
    Settled = 1
    Mixed = 2


class ReceiverSettleMode(object):
    """Settlement policy for a Receiver.

    Valid Values:
        - 0: The Receiver will spontaneously settle all incoming transfers.
        - 1: The Receiver will only settle after sending the disposition to the Sender and
          receiving a disposition indicating settlement of the delivery from the sender.

    <type name="receiver-settle-mode" class="restricted" source="ubyte">
        <choice name="first" value="0"/>
        <choice name="second" value="1"/>
    </type>
    """
    First = 0
    Second = 1


class SASLCode(object):
    """Codes to indicate the outcome of the sasl dialog.

    <type name="sasl-code" class="restricted" source="ubyte">
        <choice name="ok" value="0"/>
        <choice name="auth" value="1"/>
        <choice name="sys" value="2"/>
        <choice name="sys-perm" value="3"/>
        <choice name="sys-temp" value="4"/>
    </type>
    """
    #: Connection authentication succeeded.
    Ok = 0
    #: Connection authentication failed due to an unspecified problem with the supplied credentials.
    Auth = 1
    #: Connection authentication failed due to a system error.
    Sys = 2
    #: Connection authentication failed due to a system error that is unlikely to be corrected without intervention.
    SysPerm = 3
    #: Connection authentication failed due to a transient system error.
    SysTemp = 4


class MessageDeliveryState(object):

    WaitingToBeSent = 0
    WaitingForSendAck = 1
    Ok = 2
    Error = 3
    Timeout = 4
    Cancelled = 5


MESSAGE_DELIVERY_DONE_STATES = (
    MessageDeliveryState.Ok,
    MessageDeliveryState.Error,
    MessageDeliveryState.Timeout,
    MessageDeliveryState.Cancelled
)

class TransportType(Enum):
    """Transport type
    The underlying transport protocol type:
     Amqp: AMQP over the default TCP transport protocol, it uses port 5671.
     AmqpOverWebsocket: Amqp over the Web Sockets transport protocol, it uses
     port 443.
    """
    Amqp = 1
    AmqpOverWebsocket = 2
