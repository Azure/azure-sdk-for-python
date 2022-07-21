#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from collections import namedtuple
import sys

from .types import AMQPTypes, FieldDefinition, ObjDefinition
from .constants import FIELD

_CAN_ADD_DOCSTRING = sys.version_info.major >= 3


OpenFrame = namedtuple(
    'open',
    [
        'container_id',
        'hostname',
        'max_frame_size',
        'channel_max',
        'idle_timeout',
        'outgoing_locales',
        'incoming_locales',
        'offered_capabilities',
        'desired_capabilities',
        'properties'
    ])
OpenFrame._code = 0x00000010  # pylint:disable=protected-access
OpenFrame._definition = (  # pylint:disable=protected-access
    FIELD("container_id", AMQPTypes.string, True, None, False),
    FIELD("hostname", AMQPTypes.string, False, None, False),
    FIELD("max_frame_size", AMQPTypes.uint, False, 4294967295, False),
    FIELD("channel_max", AMQPTypes.ushort, False, 65535, False),
    FIELD("idle_timeout", AMQPTypes.uint, False, None, False),
    FIELD("outgoing_locales", AMQPTypes.symbol, False, None, True),
    FIELD("incoming_locales", AMQPTypes.symbol, False, None, True),
    FIELD("offered_capabilities", AMQPTypes.symbol, False, None, True),
    FIELD("desired_capabilities", AMQPTypes.symbol, False, None, True),
    FIELD("properties", FieldDefinition.fields, False, None, False))
if _CAN_ADD_DOCSTRING:
    OpenFrame.__doc__ = """
    OPEN performative. Negotiate Connection parameters.

    The first frame sent on a connection in either direction MUST contain an Open body.
    (Note that theConnection header which is sent first on the Connection is *not* a frame.)
    The fields indicate thecapabilities and limitations of the sending peer.

    :param str container_id: The ID of the source container.
    :param str hostname: The name of the target host.
        The dns name of the host (either fully qualified or relative) to which the sendingpeer is connecting.
        It is not mandatory to provide the hostname. If no hostname isprovided the receiving peer should select
        a default based on its own configuration.This field can be used by AMQP proxies to determine the correct
        back-end service toconnect the client to.This field may already have been specified by the sasl-init frame,
        if a SASL layer is used, or, the server name indication extension as described in RFC-4366, if a TLSlayer
        is used, in which case this field SHOULD be null or contain the same value. It is undefined what a different
        value to those already specific means.
    :param int max_frame_size: Proposed maximum frame size in bytes.
        The largest frame size that the sending peer is able to accept on this Connection.
        If this field is not set it means that the peer does not impose any specific limit. A peer MUST NOT send
        frames larger than its partner can handle. A peer that receives an oversized frame MUST close the Connection
        with the framing-error error-code. Both peers MUST accept frames of up to 512 (MIN-MAX-FRAME-SIZE)
        octets large.
    :param int channel_max: The maximum channel number that may be used on the Connection.
        The channel-max value is the highest channel number that may be used on the Connection. This value plus one
        is the maximum number of Sessions that can be simultaneously active on the Connection. A peer MUST not use
        channel numbers outside the range that its partner can handle. A peer that receives a channel number
        outside the supported range MUST close the Connection with the framing-error error-code.
    :param int idle_timeout: Idle time-out in milliseconds.
        The idle time-out required by the sender. A value of zero is the same as if it was not set (null). If the
        receiver is unable or unwilling to support the idle time-out then it should close the connection with
        an error explaining why (eg, because it is too small). If the value is not set, then the sender does not
        have an idle time-out. However, senders doing this should be aware that implementations MAY choose to use
        an internal default to efficiently manage a peer's resources.
    :param list(str) outgoing_locales: Locales available for outgoing text.
        A list of the locales that the peer supports for sending informational text. This includes Connection,
        Session and Link error descriptions. A peer MUST support at least the en-US locale. Since this value
        is always supported, it need not be supplied in the outgoing-locales. A null value or an empty list implies
        that only en-US is supported.
    :param list(str) incoming_locales: Desired locales for incoming text in decreasing level of preference.
        A list of locales that the sending peer permits for incoming informational text. This list is ordered in
        decreasing level of preference. The receiving partner will chose the first (most preferred) incoming locale
        from those which it supports. If none of the requested locales are supported, en-US will be chosen. Note
        that en-US need not be supplied in this list as it is always the fallback. A peer may determine which of the
        permitted incoming locales is chosen by examining the partner's supported locales asspecified in the
        outgoing_locales field. A null value or an empty list implies that only en-US is supported.
    :param list(str) offered_capabilities: The extension capabilities the sender supports.
        If the receiver of the offered-capabilities requires an extension capability which is not present in the
        offered-capability list then it MUST close the connection. A list of commonly defined connection capabilities
        and their meanings can be found here: http://www.amqp.org/specification/1.0/connection-capabilities.
    :param list(str) required_capabilities: The extension capabilities the sender may use if the receiver supports
        them. The desired-capability list defines which extension capabilities the sender MAY use if the receiver
        offers them (i.e. they are in the offered-capabilities list received by the sender of the
        desired-capabilities). If the receiver of the desired-capabilities offers extension capabilities which are
        not present in the desired-capability list it received, then it can be sure those (undesired) capabilities
        will not be used on the Connection.
    :param dict properties: Connection properties.
        The properties map contains a set of fields intended to indicate information about the connection and its
        container. A list of commonly defined connection properties and their meanings can be found
        here: http://www.amqp.org/specification/1.0/connection-properties.
    """


BeginFrame = namedtuple(
    'begin',
    [
        'remote_channel',
        'next_outgoing_id',
        'incoming_window',
        'outgoing_window',
        'handle_max',
        'offered_capabilities',
        'desired_capabilities',
        'properties'
    ])
BeginFrame._code = 0x00000011  # pylint:disable=protected-access
BeginFrame._definition = (  # pylint:disable=protected-access
    FIELD("remote_channel", AMQPTypes.ushort, False, None, False),
    FIELD("next_outgoing_id", AMQPTypes.uint, True, None, False),
    FIELD("incoming_window", AMQPTypes.uint, True, None, False),
    FIELD("outgoing_window", AMQPTypes.uint, True, None, False),
    FIELD("handle_max", AMQPTypes.uint, False, 4294967295, False),
    FIELD("offered_capabilities", AMQPTypes.symbol, False, None, True),
    FIELD("desired_capabilities", AMQPTypes.symbol, False, None, True),
    FIELD("properties", FieldDefinition.fields, False, None, False))
if _CAN_ADD_DOCSTRING:
    BeginFrame.__doc__ = """
    BEGIN performative. Begin a Session on a channel.

    Indicate that a Session has begun on the channel.

    :param int remote_channel: The remote channel for this Session.
        If a Session is locally initiated, the remote-channel MUST NOT be set. When an endpoint responds to a
        remotely initiated Session, the remote-channel MUST be set to the channel on which the remote Session
        sent the begin.
    :param int next_outgoing_id: The transfer-id of the first transfer id the sender will send.
        The next-outgoing-id is used to assign a unique transfer-id to all outgoing transfer frames on a given
        session. The next-outgoing-id may be initialized to an arbitrary value and is incremented after each
        successive transfer according to RFC-1982 serial number arithmetic.
    :param int incoming_window: The initial incoming-window of the sender.
        The incoming-window defines the maximum number of incoming transfer frames that the endpoint can currently
        receive. This identifies a current maximum incoming transfer-id that can be computed by subtracting one
        from the sum of incoming-window and next-incoming-id.
    :param int outgoing_window: The initial outgoing-window of the sender.
        The outgoing-window defines the maximum number of outgoing transfer frames that the endpoint can currently
        send. This identifies a current maximum outgoing transfer-id that can be computed by subtracting one from
        the sum of outgoing-window and next-outgoing-id.
    :param int handle_max: The maximum handle value that may be used on the Session.
        The handle-max value is the highest handle value that may be used on the Session. A peer MUST NOT attempt
        to attach a Link using a handle value outside the range that its partner can handle. A peer that receives
        a handle outside the supported range MUST close the Connection with the framing-error error-code.
    :param list(str) offered_capabilities: The extension capabilities the sender supports.
        A list of commonly defined session capabilities and their meanings can be found
        here: http://www.amqp.org/specification/1.0/session-capabilities.
    :param list(str) desired_capabilities: The extension capabilities the sender may use if the receiver
        supports them.
    :param dict properties: Session properties.
        The properties map contains a set of fields intended to indicate information about the session and its
        container. A list of commonly defined session properties and their meanings can be found
        here: http://www.amqp.org/specification/1.0/session-properties.
    """


AttachFrame = namedtuple(
    'attach',
    [
        'name',
        'handle',
        'role',
        'send_settle_mode',
        'rcv_settle_mode',
        'source',
        'target',
        'unsettled',
        'incomplete_unsettled',
        'initial_delivery_count',
        'max_message_size',
        'offered_capabilities',
        'desired_capabilities',
        'properties'
    ])
AttachFrame._code = 0x00000012  # pylint:disable=protected-access
AttachFrame._definition = (  # pylint:disable=protected-access
    FIELD("name", AMQPTypes.string, True, None, False),
    FIELD("handle", AMQPTypes.uint, True, None, False),
    FIELD("role", AMQPTypes.boolean, True, None, False),
    FIELD("send_settle_mode", AMQPTypes.ubyte, False, 2, False),
    FIELD("rcv_settle_mode", AMQPTypes.ubyte, False, 0, False),
    FIELD("source", ObjDefinition.source, False, None, False),
    FIELD("target", ObjDefinition.target, False, None, False),
    FIELD("unsettled", AMQPTypes.map, False, None, False),
    FIELD("incomplete_unsettled", AMQPTypes.boolean, False, False, False),
    FIELD("initial_delivery_count", AMQPTypes.uint, False, None, False),
    FIELD("max_message_size", AMQPTypes.ulong, False, None, False),
    FIELD("offered_capabilities", AMQPTypes.symbol, False, None, True),
    FIELD("desired_capabilities", AMQPTypes.symbol, False, None, True),
    FIELD("properties", FieldDefinition.fields, False, None, False))
if _CAN_ADD_DOCSTRING:
    AttachFrame.__doc__ = """
    ATTACH performative. Attach a Link to a Session.

    The attach frame indicates that a Link Endpoint has been attached to the Session. The opening flag
    is used to indicate that the Link Endpoint is newly created.

    :param str name: The name of the link.
        This name uniquely identifies the link from the container of the source to the container of the target
        node, e.g. if the container of the source node is A, and the container of the target node is B, the link
        may be globally identified by the (ordered) tuple(A,B,<name>).
    :param int handle: The handle of the link.
        The handle MUST NOT be used for other open Links. An attempt to attach using a handle which is already
        associated with a Link MUST be responded to with an immediate close carrying a Handle-in-usesession-error.
        To make it easier to monitor AMQP link attach frames, it is recommended that implementations always assign
        the lowest available handle to this field.
    :param bool role: The role of the link endpoint. Either Role.Sender (False) or Role.Receiver (True).
    :param str send_settle_mode: The settlement mode for the Sender.
        Determines the settlement policy for deliveries sent at the Sender. When set at the Receiver this indicates
        the desired value for the settlement mode at the Sender. When set at the Sender this indicates the actual
        settlement mode in use.
    :param str rcv_settle_mode: The settlement mode of the Receiver.
        Determines the settlement policy for unsettled deliveries received at the Receiver. When set at the Sender
        this indicates the desired value for the settlement mode at the Receiver. When set at the Receiver this
        indicates the actual settlement mode in use.
    :param ~uamqp.messaging.Source source: The source for Messages.
        If no source is specified on an outgoing Link, then there is no source currently attached to the Link.
        A Link with no source will never produce outgoing Messages.
    :param ~uamqp.messaging.Target target: The target for Messages.
        If no target is specified on an incoming Link, then there is no target currently attached to the Link.
        A Link with no target will never permit incoming Messages.
    :param dict unsettled: Unsettled delivery state.
        This is used to indicate any unsettled delivery states when a suspended link is resumed. The map is keyed
        by delivery-tag with values indicating the delivery state. The local and remote delivery states for a given
        delivery-tag MUST be compared to resolve any in-doubt deliveries. If necessary, deliveries MAY be resent,
        or resumed based on the outcome of this comparison. If the local unsettled map is too large to be encoded
        within a frame of the agreed maximum frame size then the session may be ended with the
        frame-size-too-smallerror. The endpoint SHOULD make use of the ability to send an incomplete unsettled map
        to avoid sending an error. The unsettled map MUST NOT contain null valued keys. When reattaching
        (as opposed to resuming), the unsettled map MUST be null.
    :param bool incomplete_unsettled:
        If set to true this field indicates that the unsettled map provided is not complete. When the map is
        incomplete the recipient of the map cannot take the absence of a delivery tag from the map as evidence of
        settlement. On receipt of an incomplete unsettled map a sending endpoint MUST NOT send any new deliveries
        (i.e. deliveries where resume is not set to true) to its partner (and a receiving endpoint which sent an
        incomplete unsettled map MUST detach with an error on receiving a transfer which does not have the resume
        flag set to true).
    :param int initial_delivery_count: This MUST NOT be null if role is sender,
        and it is ignored if the role is receiver.
    :param int max_message_size: The maximum message size supported by the link endpoint.
        This field indicates the maximum message size supported by the link endpoint. Any attempt to deliver a
        message larger than this results in a message-size-exceeded link-error. If this field is zero or unset,
        there is no maximum size imposed by the link endpoint.
    :param list(str) offered_capabilities: The extension capabilities the sender supports.
        A list of commonly defined session capabilities and their meanings can be found
        here: http://www.amqp.org/specification/1.0/link-capabilities.
    :param list(str) desired_capabilities: The extension capabilities the sender may use if the receiver
        supports them.
    :param dict properties: Link properties.
        The properties map contains a set of fields intended to indicate information about the link and its
        container. A list of commonly defined link properties and their meanings can be found
        here: http://www.amqp.org/specification/1.0/link-properties.
    """


FlowFrame = namedtuple(
    'flow',
    [
        'next_incoming_id',
        'incoming_window',
        'next_outgoing_id',
        'outgoing_window',
        'handle',
        'delivery_count',
        'link_credit',
        'available',
        'drain',
        'echo',
        'properties'
    ])
FlowFrame.__new__.__defaults__ = (None, None, None, None, None, None, None)
FlowFrame._code = 0x00000013  # pylint:disable=protected-access
FlowFrame._definition = (  # pylint:disable=protected-access
    FIELD("next_incoming_id", AMQPTypes.uint, False, None, False),
    FIELD("incoming_window", AMQPTypes.uint, True, None, False),
    FIELD("next_outgoing_id", AMQPTypes.uint, True, None, False),
    FIELD("outgoing_window", AMQPTypes.uint, True, None, False),
    FIELD("handle", AMQPTypes.uint, False, None, False),
    FIELD("delivery_count", AMQPTypes.uint, False, None, False),
    FIELD("link_credit", AMQPTypes.uint, False, None, False),
    FIELD("available", AMQPTypes.uint, False, None, False),
    FIELD("drain", AMQPTypes.boolean, False, False, False),
    FIELD("echo", AMQPTypes.boolean, False, False, False),
    FIELD("properties", FieldDefinition.fields, False, None, False))
if _CAN_ADD_DOCSTRING:
    FlowFrame.__doc__ = """
    FLOW performative. Update link state.

    Updates the flow state for the specified Link.

    :param int next_incoming_id: Identifies the expected transfer-id of the next incoming transfer frame.
        This value is not set if and only if the sender has not yet received the begin frame for the session.
    :param int incoming_window: Defines the maximum number of incoming transfer frames that the endpoint
        concurrently receive.
    :param int next_outgoing_id: The transfer-id that will be assigned to the next outgoing transfer frame.
    :param int outgoing_window: Defines the maximum number of outgoing transfer frames that the endpoint could
        potentially currently send, if it was not constrained by restrictions imposed by its peer's incoming-window.
    :param int handle: If set, indicates that the flow frame carries flow state information for the local Link
        Endpoint associated with the given handle. If not set, the flow frame is carrying only information
        pertaining to the Session Endpoint. If set to a handle that is not currently associated with an attached
        Link, the recipient MUST respond by ending the session with an unattached-handle session error.
    :param int delivery_count: The endpoint's delivery-count.
        When the handle field is not set, this field MUST NOT be set. When the handle identifies that the flow
        state is being sent from the Sender Link Endpoint to Receiver Link Endpoint this field MUST be set to the
        current delivery-count of the Link Endpoint. When the flow state is being sent from the Receiver Endpoint
        to the Sender Endpoint this field MUST be set to the last known value of the corresponding Sending Endpoint.
        In the event that the Receiving Link Endpoint has not yet seen the initial attach frame from the Sender
        this field MUST NOT be set.
    :param int link_credit: The current maximum number of Messages that can be received.
        The current maximum number of Messages that can be handled at the Receiver Endpoint of the Link. Only the
        receiver endpoint can independently set this value. The sender endpoint sets this to the last known
        value seen from the receiver. When the handle field is not set, this field MUST NOT be set.
    :param int available: The number of available Messages.
        The number of Messages awaiting credit at the link sender endpoint. Only the sender can independently set
        this value. The receiver sets this to the last known value seen from the sender. When the handle field is
        not set, this field MUST NOT be set.
    :param bool drain: Indicates drain mode.
        When flow state is sent from the sender to the receiver, this field contains the actual drain mode of the
        sender. When flow state is sent from the receiver to the sender, this field contains the desired drain
        mode of the receiver. When the handle field is not set, this field MUST NOT be set.
    :param bool echo: Request link state from other endpoint.
    :param dict properties: Link state properties.
        A list of commonly defined link state properties and their meanings can be found
        here: http://www.amqp.org/specification/1.0/link-state-properties.
    """


TransferFrame = namedtuple(
    'transfer',
    [
        'handle',
        'delivery_id',
        'delivery_tag',
        'message_format',
        'settled',
        'more',
        'rcv_settle_mode',
        'state',
        'resume',
        'aborted',
        'batchable',
        'payload'
    ])
TransferFrame._code = 0x00000014  # pylint:disable=protected-access
TransferFrame._definition = (  # pylint:disable=protected-access
    FIELD("handle", AMQPTypes.uint, True, None, False),
    FIELD("delivery_id", AMQPTypes.uint, False, None, False),
    FIELD("delivery_tag", AMQPTypes.binary, False, None, False),
    FIELD("message_format", AMQPTypes.uint, False, 0, False),
    FIELD("settled", AMQPTypes.boolean, False, None, False),
    FIELD("more", AMQPTypes.boolean, False, False, False),
    FIELD("rcv_settle_mode", AMQPTypes.ubyte, False, None, False),
    FIELD("state", ObjDefinition.delivery_state, False, None, False),
    FIELD("resume", AMQPTypes.boolean, False, False, False),
    FIELD("aborted", AMQPTypes.boolean, False, False, False),
    FIELD("batchable", AMQPTypes.boolean, False, False, False),
    None)
if _CAN_ADD_DOCSTRING:
    TransferFrame.__doc__ = """
    TRANSFER performative. Transfer a Message.

    The transfer frame is used to send Messages across a Link. Messages may be carried by a single transfer up
    to the maximum negotiated frame size for the Connection. Larger Messages may be split across several
    transfer frames.

    :param int handle: Specifies the Link on which the Message is transferred.
    :param int delivery_id: Alias for delivery-tag.
        The delivery-id MUST be supplied on the first transfer of a multi-transfer delivery. On continuation
        transfers the delivery-id MAY be omitted. It is an error if the delivery-id on a continuation transfer
        differs from the delivery-id on the first transfer of a delivery.
    :param bytes delivery_tag: Uniquely identifies the delivery attempt for a given Message on this Link.
        This field MUST be specified for the first transfer of a multi transfer message and may only be
        omitted for continuation transfers.
    :param int message_format: Indicates the message format.
        This field MUST be specified for the first transfer of a multi transfer message and may only be omitted
        for continuation transfers.
    :param bool settled: If not set on the first (or only) transfer for a delivery, then the settled flag MUST
        be interpreted as being false. For subsequent transfers if the settled flag is left unset then it MUST be
        interpreted as true if and only if the value of the settled flag on any of the preceding transfers was
        true; if no preceding transfer was sent with settled being true then the value when unset MUST be taken
        as false. If the negotiated value for snd-settle-mode at attachment is settled, then this field MUST be
        true on at least one transfer frame for a delivery (i.e. the delivery must be settled at the Sender at
        the point the delivery has been completely transferred). If the negotiated value for snd-settle-mode at
        attachment is unsettled, then this field MUST be false (or unset) on every transfer frame for a delivery
        (unless the delivery is aborted).
    :param bool more: Indicates that the Message has more content.
        Note that if both the more and aborted fields are set to true, the aborted flag takes precedence. That is
        a receiver should ignore the value of the more field if the transfer is marked as aborted. A sender
        SHOULD NOT set the more flag to true if it also sets the aborted flag to true.
    :param str rcv_settle_mode: If first, this indicates that the Receiver MUST settle the delivery once it has
        arrived without waiting for the Sender to settle first. If second, this indicates that the Receiver MUST
        NOT settle until sending its disposition to the Sender and receiving a settled disposition from the sender.
        If not set, this value is defaulted to the value negotiated on link attach. If the negotiated link value is
        first, then it is illegal to set this field to second. If the message is being sent settled by the Sender,
        the value of this field is ignored. The (implicit or explicit) value of this field does not form part of the
        transfer state, and is not retained if a link is suspended and subsequently resumed.
    :param bytes state: The state of the delivery at the sender.
        When set this informs the receiver of the state of the delivery at the sender. This is particularly useful
        when transfers of unsettled deliveries are resumed after a resuming a link. Setting the state on the
        transfer can be thought of as being equivalent to sending a disposition immediately before the transfer
        performative, i.e. it is the state of the delivery (not the transfer) that existed at the point the frame
        was sent. Note that if the transfer performative (or an earlier disposition performative referring to the
        delivery) indicates that the delivery has attained a terminal state, then no future transfer or disposition
        sent by the sender can alter that terminal state.
    :param bool resume: Indicates a resumed delivery.
        If true, the resume flag indicates that the transfer is being used to reassociate an unsettled delivery
        from a dissociated link endpoint. The receiver MUST ignore resumed deliveries that are not in its local
        unsettled map. The sender MUST NOT send resumed transfers for deliveries not in its local unsettledmap.
        If a resumed delivery spans more than one transfer performative, then the resume flag MUST be set to true
        on the first transfer of the resumed delivery. For subsequent transfers for the same delivery the resume
        flag may be set to true, or may be omitted. In the case where the exchange of unsettled maps makes clear
        that all message data has been successfully transferred to the receiver, and that only the final state
        (andpotentially settlement) at the sender needs to be conveyed, then a resumed delivery may carry no
        payload and instead act solely as a vehicle for carrying the terminal state of the delivery at the sender.
    :param bool aborted: Indicates that the Message is aborted.
        Aborted Messages should be discarded by the recipient (any payload within the frame carrying the performative
        MUST be ignored). An aborted Message is implicitly settled.
    :param bool batchable: Batchable hint.
        If true, then the issuer is hinting that there is no need for the peer to urgently communicate updated
        delivery state. This hint may be used to artificially increase the amount of batching an implementation
        uses when communicating delivery states, and thereby save bandwidth. If the message being delivered is too
        large to fit within a single frame, then the setting of batchable to true on any of the transfer
        performatives for the delivery is equivalent to setting batchable to true for all the transfer performatives
        for the delivery. The batchable value does not form part of the transfer state, and is not retained if a
        link is suspended and subsequently resumed.
    """


DispositionFrame = namedtuple(
    'disposition',
    [
        'role',
        'first',
        'last',
        'settled',
        'state',
        'batchable'
    ])
DispositionFrame._code = 0x00000015  # pylint:disable=protected-access
DispositionFrame._definition = (  # pylint:disable=protected-access
    FIELD("role", AMQPTypes.boolean, True, None, False),
    FIELD("first", AMQPTypes.uint, True, None, False),
    FIELD("last", AMQPTypes.uint, False, None, False),
    FIELD("settled", AMQPTypes.boolean, False, False, False),
    FIELD("state", ObjDefinition.delivery_state, False, None, False),
    FIELD("batchable", AMQPTypes.boolean, False, False, False))
if _CAN_ADD_DOCSTRING:
    DispositionFrame.__doc__ = """
    DISPOSITION performative. Inform remote peer of delivery state changes.

    The disposition frame is used to inform the remote peer of local changes in the state of deliveries.
    The disposition frame may reference deliveries from many different links associated with a session,
    although all links MUST have the directionality indicated by the specified role. Note that it is possible
    for a disposition sent from sender to receiver to refer to a delivery which has not yet completed
    (i.e. a delivery which is spread over multiple frames and not all frames have yet been sent). The use of such
    interleaving is discouraged in favor of carrying the modified state on the next transfer performative for
    the delivery. The disposition performative may refer to deliveries on links that are no longer attached.
    As long as the links have not been closed or detached with an error then the deliveries are still "live" and
    the updated state MUST be applied.

    :param str role: Directionality of disposition.
        The role identifies whether the disposition frame contains information about sending link endpoints
        or receiving link endpoints.
    :param int first: Lower bound of deliveries.
        Identifies the lower bound of delivery-ids for the deliveries in this set.
    :param int last: Upper bound of deliveries.
        Identifies the upper bound of delivery-ids for the deliveries in this set. If not set,
        this is taken to be the same as first.
    :param bool settled: Indicates deliveries are settled.
        If true, indicates that the referenced deliveries are considered settled by the issuing endpoint.
    :param bytes state: Indicates state of deliveries.
        Communicates the state of all the deliveries referenced by this disposition.
    :param bool batchable: Batchable hint.
        If true, then the issuer is hinting that there is no need for the peer to urgently communicate the impact
        of the updated delivery states. This hint may be used to artificially increase the amount of batching an
        implementation uses when communicating delivery states, and thereby save bandwidth.
    """

DetachFrame = namedtuple('detach', ['handle', 'closed', 'error'])
DetachFrame._code = 0x00000016  # pylint:disable=protected-access
DetachFrame._definition = (  # pylint:disable=protected-access
    FIELD("handle", AMQPTypes.uint, True, None, False),
    FIELD("closed", AMQPTypes.boolean, False, False, False),
    FIELD("error", ObjDefinition.error, False, None, False))
if _CAN_ADD_DOCSTRING:
    DetachFrame.__doc__ = """
    DETACH performative. Detach the Link Endpoint from the Session.

    Detach the Link Endpoint from the Session. This un-maps the handle and makes it available for
    use by other Links

    :param int handle: The local handle of the link to be detached.
    :param bool handle: If true then the sender has closed the link.
    :param ~uamqp.error.AMQPError error: Error causing the detach.
        If set, this field indicates that the Link is being detached due to an error condition.
        The value of the field should contain details on the cause of the error.
    """


EndFrame = namedtuple('end', ['error'])
EndFrame._code = 0x00000017  # pylint:disable=protected-access
EndFrame._definition = (FIELD("error", ObjDefinition.error, False, None, False),)  # pylint:disable=protected-access
if _CAN_ADD_DOCSTRING:
    EndFrame.__doc__ = """
    END performative. End the Session.

    Indicates that the Session has ended.

    :param ~uamqp.error.AMQPError error: Error causing the end.
        If set, this field indicates that the Session is being ended due to an error condition.
        The value of the field should contain details on the cause of the error.
    """


CloseFrame = namedtuple('close', ['error'])
CloseFrame._code = 0x00000018  # pylint:disable=protected-access
CloseFrame._definition = (FIELD("error", ObjDefinition.error, False, None, False),)  # pylint:disable=protected-access
if _CAN_ADD_DOCSTRING:
    CloseFrame.__doc__ = """
    CLOSE performative. Signal a Connection close.

    Sending a close signals that the sender will not be sending any more frames (or bytes of any other kind) on
    the Connection. Orderly shutdown requires that this frame MUST be written by the sender. It is illegal to
    send any more frames (or bytes of any other kind) after sending a close frame.

    :param ~uamqp.error.AMQPError error: Error causing the close.
        If set, this field indicates that the Connection is being closed due to an error condition.
        The value of the field should contain details on the cause of the error.
    """


SASLMechanism = namedtuple('sasl_mechanism', ['sasl_server_mechanisms'])
SASLMechanism._code = 0x00000040  # pylint:disable=protected-access
SASLMechanism._definition = (FIELD('sasl_server_mechanisms', AMQPTypes.symbol, True, None, True),)  # pylint:disable=protected-access
if _CAN_ADD_DOCSTRING:
    SASLMechanism.__doc__ = """
    Advertise available sasl mechanisms.

    dvertises the available SASL mechanisms that may be used for authentication.

    :param list(bytes) sasl_server_mechanisms: Supported sasl mechanisms.
        A list of the sasl security mechanisms supported by the sending peer.
        It is invalid for this list to be null or empty. If the sending peer does not require its partner to
        authenticate with it, then it should send a list of one element with its value as the SASL mechanism
        ANONYMOUS. The server mechanisms are ordered in decreasing level of preference.
    """


SASLInit = namedtuple('sasl_init', ['mechanism', 'initial_response', 'hostname'])
SASLInit._code = 0x00000041  # pylint:disable=protected-access
SASLInit._definition = (  # pylint:disable=protected-access
    FIELD('mechanism', AMQPTypes.symbol, True, None, False),
    FIELD('initial_response', AMQPTypes.binary, False, None, False),
    FIELD('hostname', AMQPTypes.string, False, None, False))
if _CAN_ADD_DOCSTRING:
    SASLInit.__doc__ = """
    Initiate sasl exchange.

    Selects the sasl mechanism and provides the initial response if needed.

    :param bytes mechanism: Selected security mechanism.
        The name of the SASL mechanism used for the SASL exchange. If the selected mechanism is not supported by
        the receiving peer, it MUST close the Connection with the authentication-failure close-code. Each peer
        MUST authenticate using the highest-level security profile it can handle from the list provided by the
        partner.
    :param bytes initial_response: Security response data.
        A block of opaque data passed to the security mechanism. The contents of this data are defined by the
        SASL security mechanism.
    :param str hostname: The name of the target host.
        The DNS name of the host (either fully qualified or relative) to which the sending peer is connecting. It
        is not mandatory to provide the hostname. If no hostname is provided the receiving peer should select a
        default based on its own configuration. This field can be used by AMQP proxies to determine the correct
        back-end service to connect the client to, and to determine the domain to validate the client's credentials
        against. This field may already have been specified by the server name indication extension as described
        in RFC-4366, if a TLS layer is used, in which case this field SHOULD benull or contain the same value.
        It is undefined what a different value to those already specific means.
    """


SASLChallenge = namedtuple('sasl_challenge', ['challenge'])
SASLChallenge._code = 0x00000042  # pylint:disable=protected-access
SASLChallenge._definition = (FIELD('challenge', AMQPTypes.binary, True, None, False),)  # pylint:disable=protected-access
if _CAN_ADD_DOCSTRING:
    SASLChallenge.__doc__ = """
    Security mechanism challenge.

    Send the SASL challenge data as defined by the SASL specification.

    :param bytes challenge: Security challenge data.
        Challenge information, a block of opaque binary data passed to the security mechanism.
    """


SASLResponse = namedtuple('sasl_response', ['response'])
SASLResponse._code = 0x00000043  # pylint:disable=protected-access
SASLResponse._definition = (FIELD('response', AMQPTypes.binary, True, None, False),)  # pylint:disable=protected-access
if _CAN_ADD_DOCSTRING:
    SASLResponse.__doc__ = """
    Security mechanism response.

    Send the SASL response data as defined by the SASL specification.

    :param bytes response: Security response data.
    """


SASLOutcome = namedtuple('sasl_outcome', ['code', 'additional_data'])
SASLOutcome._code = 0x00000044  # pylint:disable=protected-access
SASLOutcome._definition = (  # pylint:disable=protected-access
    FIELD('code', AMQPTypes.ubyte, True, None, False),
    FIELD('additional_data', AMQPTypes.binary, False, None, False))
if _CAN_ADD_DOCSTRING:
    SASLOutcome.__doc__ = """
    Indicates the outcome of the sasl dialog.

    This frame indicates the outcome of the SASL dialog. Upon successful completion of the SASL dialog the
    Security Layer has been established, and the peers must exchange protocol headers to either starta nested
    Security Layer, or to establish the AMQP Connection.

    :param int code: Indicates the outcome of the sasl dialog.
        A reply-code indicating the outcome of the SASL dialog.
    :param bytes additional_data: Additional data as specified in RFC-4422.
        The additional-data field carries additional data on successful authentication outcomeas specified by
        the SASL specification (RFC-4422). If the authentication is unsuccessful, this field is not set.
    """
