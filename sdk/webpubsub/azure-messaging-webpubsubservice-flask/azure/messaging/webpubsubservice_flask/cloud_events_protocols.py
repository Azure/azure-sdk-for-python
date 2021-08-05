from dataclasses import dataclass
import dataclasses

@dataclass(init=False)
class ConnectionContext:
    hub: str
    connection_id: str
    event_name: str
    origin: str = None
    user_id: str = None
    subprotocol: str = None
    states: dict[str, object] = None

    def __init__(self, **kwargs):
      fields = set([f.name for f in dataclasses.fields(self)])
      for k, v in kwargs.items():
        if k in fields:
          setattr(self, k, v) 

@dataclass(init=False)
class Certificate:
    thumbprint: str

    def __init__(self, **kwargs):
      fields = set([f.name for f in dataclasses.fields(self)])
      for k, v in kwargs.items():
        if k in fields:
          setattr(self, k, v) 

@dataclass(init=False)
class ConnectResponse:
    groups: list[str] = None
    roles: list[str] = None
    user_id: str = None
    subprotocol: str = None

    def __init__(self, **kwargs):
      fields = set([f.name for f in dataclasses.fields(self)])
      for k, v in kwargs.items():
        if k in fields:
          setattr(self, k, v) 

@dataclass(init=False)
class ConnectResquest:
    context: ConnectionContext
    claims: dict[str, list[str]] = None
    queries: dict[str, list[str]] = None
    subprotocols: list[str] = None
    client_certificates: list[Certificate] = None
    
    def __init__(self, **kwargs):
      fields = set([f.name for f in dataclasses.fields(self)])
      for k, v in kwargs.items():
        if k in fields:
          setattr(self, k, v) 

@dataclass(init=False)
class ConnectedRequest:
    context: ConnectionContext

    def __init__(self, **kwargs):
      fields = set([f.name for f in dataclasses.fields(self)])
      for k, v in kwargs.items():
        if k in fields:
          setattr(self, k, v) 

@dataclass(init=False)
class DisconnectedRequest:
    context: ConnectionContext
    reason: str = None

    def __init__(self, **kwargs):
      fields = set([f.name for f in dataclasses.fields(self)])
      for k, v in kwargs.items():
        if k in fields:
          setattr(self, k, v) 
