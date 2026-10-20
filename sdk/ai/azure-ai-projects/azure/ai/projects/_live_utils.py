# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Shared protocol metadata for the handwritten Live clients.

Foundry constructs session.start from the persisted agent definition. Live uses
its own event vocabulary; Realtime response.cancel and audio-buffer commands
must not be synthesized on this connection.
"""

import json
import logging
from typing import Any, Mapping, Optional, Type, Union

from . import models
from ._realtime import _to_ws_url, _USER_AGENT
from ._utils.model_base import Model, SdkJSONEncoder

LiveClientEvent = Union[models.LiveClientEvent, str, Mapping[str, Any]]
LiveServerEvent = Union[models.LiveServerEvent, Mapping[str, Any]]
_LOGGER = logging.getLogger("azure.ai.projects.live")


def _server_event_types() -> dict[str, Type[Model]]:
    result: dict[str, Type[Model]] = {}
    for name, cls in models.LiveServerEvent.__mapping__.items():
        if isinstance(cls, type) and issubclass(cls, Model):
            result[name] = cls
    return result


_SERVER_EVENT_TYPES = _server_event_types()


def _live_url(endpoint: str, agent_name: str) -> str:
    return _to_ws_url(endpoint, agent_name) + "/live/sessions"


def _live_query(
    api_version: str,
    agent_version: Optional[str],
    structured_inputs: Optional[Mapping[str, Any]],
    store: Optional[bool],
    extra_query: Mapping[str, str],
) -> dict[str, str]:
    result = {"api-version": api_version, "x-ms-client-sdk": _USER_AGENT}
    result.update(extra_query)
    if agent_version is not None:
        result["x-agent-version-override"] = agent_version
    if structured_inputs is not None:
        if "structured_input" in result:
            raise ValueError("structured_input and structured_inputs cannot be supplied together.")
        result["structured_inputs"] = json.dumps(structured_inputs, cls=SdkJSONEncoder)
    if "structured_inputs" in result and "structured_input" in result:
        raise ValueError("structured_input and structured_inputs cannot be supplied together.")
    if store is not None:
        result["store"] = str(store).lower()
    return result


def _event(
    model: Type[models.LiveClientEvent], event_id: Optional[str] = None, **fields: Any
) -> models.LiveClientEvent:
    if event_id is not None:
        fields["event_id"] = event_id
    return model(fields)
