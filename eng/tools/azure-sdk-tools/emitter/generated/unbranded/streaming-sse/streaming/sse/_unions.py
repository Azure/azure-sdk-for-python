# coding=utf-8

from typing import Literal, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .named import models as _named_models1
    from .protocol import models as _protocol_models1
    from .protocol.data import models as _protocol_data_models2
    from .retrieve import models as _retrieve_models1
    from .unnamed import models as _unnamed_models1
UnnamedEvents = "_unnamed_models1.Info"
ResponseEvents = Union["_named_models1.ResponseCreated", "_named_models1.ResponseDelta", Literal["[DONE]"]]
RetrievalEvents = Union["_retrieve_models1.PartialResult", "_retrieve_models1.FinalResult", Literal["[DONE]"]]
ProtocolEvents = "_protocol_models1.Info"
DataEvents = Union["_protocol_data_models2.WithEnvelope", "_protocol_data_models2.WithEnvelope1"]
