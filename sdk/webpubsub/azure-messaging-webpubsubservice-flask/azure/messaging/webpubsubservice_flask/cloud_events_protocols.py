from dataclasses import dataclass

@dataclass(init=False)
class ConnectionContext:
    hub: str
    connection_id: str
    event_name: str
    type: str
    origin: str = None
    user_id: str = None
    subprotocol: str = None
    states: dict[str, object] = None

    def __init__(self, hub: str, connection_id: str, event_name: str, type: str, origin: str = None, user_id: str = None, subprotocol: str = None, states: dict[str, object] = None, **kwargs):
      self.hub = hub
      self.connection_id = connection_id
      self.event_name = event_name
      self.type = type
      self.origin = origin
      self.user_id = user_id
      self.subprotocol = subprotocol
      self.states = states

@dataclass(init=False)
class Certificate:
    thumbprint: str

    def __init__(self, thumbprint: str, **kwargs):
      self.thumbprint = thumbprint

@dataclass(init=False)
class ConnectResponse:
    groups: list[str] = None
    roles: list[str] = None
    user_id: str = None
    subprotocol: str = None

    def __init__(self, groups: list[str] = None, roles: list[str] = None, user_id: str = None, subprotocol: str = None, **kwargs):
      self.groups = groups
      self.roles = roles
      self.user_id = user_id
      self.subprotocol = subprotocol

@dataclass(init=False)
class ConnectResquest:
    claims: dict[str, list[str]] = None
    queries: dict[str, list[str]] = None
    subprotocols: list[str] = None
    client_certificates: list[Certificate] = None
    
    def __init__(self, claims: dict[str, list[str]] = None, queries: dict[str, list[str]] = None, subprotocols: list[str] = None, client_certificates: list[Certificate] = None, **kwargs):
      self.claims = claims
      self.queries = queries
      self.subprotocols = subprotocols
      self.client_certificates = client_certificates


@dataclass(init=False)
class DisconnectedRequest:
    reason: str = None

    def __init__(self, reason: str = None, **kwargs):
      self.reason = reason
