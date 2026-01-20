# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Optional, Union, overload

from langchain_core.language_models import BaseChatModel

from azure.ai.agentserver.core.tools import FoundryToolLike
from ._chat_model import FoundryToolLateBindingChatModel
from ._middleware import FoundryToolBindingMiddleware
from ._resolver import get_registry


@overload
def use_foundry_tools(tools: List[FoundryToolLike], /) -> FoundryToolBindingMiddleware:  # pylint: disable=C4743
    """Use foundry tools as middleware.

    :param tools: A list of foundry tools to bind.
    :type tools: List[FoundryToolLike]
    :return: A FoundryToolBindingMiddleware that binds the given tools.
    :rtype: FoundryToolBindingMiddleware
    """
    ...


@overload
def use_foundry_tools(model: BaseChatModel, tools: List[FoundryToolLike], /) -> FoundryToolLateBindingChatModel:  # pylint: disable=C4743
    """Use foundry tools with a chat model.

    :param model: The chat model to bind the tools to.
    :type model: BaseChatModel
    :param tools: A list of foundry tools to bind.
    :type tools: List[FoundryToolLike]
    :return: A FoundryToolLateBindingChatModel that binds the given tools to the model.
    :rtype: FoundryToolLateBindingChatModel
    """
    ...


def use_foundry_tools(  # pylint: disable=C4743
        model_or_tools: Union[BaseChatModel, List[FoundryToolLike]],
        tools: Optional[List[FoundryToolLike]] = None,
        /,
) -> Union[FoundryToolBindingMiddleware, FoundryToolLateBindingChatModel]:
    """Use foundry tools with a chat model or as middleware.

    :param model_or_tools: The chat model to bind the tools to, or a list of foundry tools to bind as middleware.
    :type model_or_tools: Union[BaseChatModel, List[FoundryToolLike]]
    :param tools: A list of foundry tools to bind (required if model_or_tools is a chat model).
    :type tools: Optional[List[FoundryToolLike]]
    :return: A FoundryToolLateBindingChatModel or FoundryToolBindingMiddleware that binds the given tools.
    :rtype: Union[FoundryToolBindingMiddleware, FoundryToolLateBindingChatModel]
    """
    if isinstance(model_or_tools, BaseChatModel):
        if tools is None:
            raise ValueError("Tools must be provided when a model is given.")
        get_registry().extend(tools)
        return FoundryToolLateBindingChatModel(model_or_tools, foundry_tools=tools)
    get_registry().extend(model_or_tools)
    return FoundryToolBindingMiddleware(model_or_tools)
