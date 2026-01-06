# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any
from ...logger import get_logger
from ...models import CreateResponse
from ...models.projects import AgentId, AgentReference, ResponseConversation1
from .id_generator.foundry_id_generator import FoundryIdGenerator
from .id_generator.id_generator import IdGenerator
from ...tools import UserInfo

logger = get_logger()


class AgentRunContext:
    def __init__(self, payload: dict, **kwargs: Any) -> None:
        self._raw_payload = payload
        self._request = _deserialize_create_response(payload)
        self._id_generator = FoundryIdGenerator.from_request(payload)
        self._response_id = self._id_generator.response_id
        self._conversation_id = self._id_generator.conversation_id
        self._stream = self.request.get("stream", False)
        self._user_info = kwargs.get("user_info", None)
        self._agent_tools = kwargs.get("agent_tools", [])

    @property
    def raw_payload(self) -> dict:
        return self._raw_payload

    @property
    def request(self) -> CreateResponse:
        return self._request

    @property
    def id_generator(self) -> IdGenerator:
        return self._id_generator

    @property
    def response_id(self) -> str:
        return self._response_id

    @property
    def conversation_id(self) -> str:
        return self._conversation_id

    @property
    def stream(self) -> bool:
        return self._stream

    def get_agent_id_object(self) -> AgentId:
        agent = self.request.get("agent")
        if not agent:
            return None  # type: ignore
        return AgentId(
            {
                "type": agent.type,
                "name": agent.name,
                "version": agent.version,
            }
        )

    def get_conversation_object(self) -> ResponseConversation1:
        if not self._conversation_id:
            return None  # type: ignore
        return ResponseConversation1(id=self._conversation_id)

    def get_tools(self) -> list:
        # request tools take precedence over agent tools
        request_tools = self.request.get("tools", [])
        if not request_tools:
            return self._agent_tools
        return request_tools

    def get_user_info(self) -> UserInfo:
        return self._user_info


def _deserialize_create_response(payload: dict) -> CreateResponse:
    _deserialized = CreateResponse(**payload)

    raw_agent_reference = payload.get("agent")
    if raw_agent_reference:
        _deserialized["agent"] = _deserialize_agent_reference(raw_agent_reference)

    tools = payload.get("tools")
    if tools:
        _deserialized["tools"] = [tool for tool in tools]  # pylint: disable=unnecessary-comprehension
    return _deserialized


def _deserialize_agent_reference(payload: dict) -> AgentReference:
    if not payload:
        return None  # type: ignore
    return AgentReference(**payload)
