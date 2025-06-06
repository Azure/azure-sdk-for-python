# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import contextvars
from typing import Optional

# Context variable to pass user_agent to evaluators
_current_user_agent: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_user_agent', default=None)

def get_current_user_agent() -> Optional[str]:
    """Get the current user agent from context.
    
    :return: The current user agent if set, None otherwise.
    :rtype: Optional[str]
    """
    return _current_user_agent.get()

def set_current_user_agent(user_agent: Optional[str]) -> contextvars.Token:
    """Set the current user agent in context.
    
    :param user_agent: The user agent to set.
    :type user_agent: Optional[str]
    :return: A token that can be used to reset the context.
    :rtype: contextvars.Token
    """
    return _current_user_agent.set(user_agent)