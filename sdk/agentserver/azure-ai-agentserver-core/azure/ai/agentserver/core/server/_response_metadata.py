# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Dict

from ..application._metadata import get_current_app
from ..models import Response as OpenAIResponse, ResponseStreamEvent
from ..models.projects import (
    ResponseCompletedEvent,
    ResponseCreatedEvent,
    ResponseInProgressEvent,
)

HEADER_NAME = "x-aml-foundry-agents-metadata"
METADATA_KEY = "foundry_agents_metadata"


def _metadata_json() -> str:
    payload = asdict(get_current_app())
    return json.dumps(payload)


def build_foundry_agents_metadata_headers() -> Dict[str, str]:
    """
    Return header dict containing the foundry metadata header.
    
    :return: A dictionary with the foundry metadata header.
    :rtype: Dict[str, str]
    """
    return {HEADER_NAME: _metadata_json()}


def attach_foundry_metadata_to_response(response: OpenAIResponse) -> None:
    """
    Attach metadata into response.metadata[METADATA_KEY].
    
    :param response: The OpenAIResponse object to attach metadata to.
    :type response: OpenAIResponse
    :return: None
    :rtype: None
    """
    meta = response.metadata or {}
    meta[METADATA_KEY] = _metadata_json()
    response.metadata = meta


def try_attach_foundry_metadata_to_event(event: ResponseStreamEvent) -> None:
    """
    Attach metadata to supported stream events; skip others.
    
    :param event: The ResponseStreamEvent object to attach metadata to.
    :type event: ResponseStreamEvent
    :return: None
    :rtype: None
    """
    if isinstance(event, (ResponseCreatedEvent, ResponseInProgressEvent, ResponseCompletedEvent)):
        attach_foundry_metadata_to_response(event.response)
