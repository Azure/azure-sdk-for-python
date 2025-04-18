# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Original source code: promptflow-tracing/promptflow/tracing/_integrations/_openai_injector.py

import functools
import importlib
import logging

from contextvars import ContextVar
from typing import Any, Callable, Final, Generator, Optional, Protocol, Sequence, Tuple

from azure.ai.evaluation._legacy._adapters._errors import MissingRequiredPackage
from azure.ai.evaluation._legacy._batch_engine._result import TokenMetrics


_token_metrics: ContextVar[TokenMetrics] = ContextVar("token_metrics", default=TokenMetrics(0, 0, 0))
KEY_ATTR_ORIGINAL: Final[str] = "_original"


class _TokenMetrics(Protocol):
    """Protocol class to represent the token metrics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class _WithUsage(Protocol):
    """Protocol class to represent an OpenAI object that may have a token usage property/attribute."""

    usage: Optional[_TokenMetrics]


def _wrap_openai_api_method(method: Callable, is_async: bool) -> Callable:
    """Wraps the OpenAI API method to inject logic to run on the result of the call."""

    def update_usage(result: _WithUsage) -> None:
        if hasattr(result, "usage") and result.usage is not None:
            usage = _token_metrics.get()
            usage.prompt_tokens += result.usage.prompt_tokens
            usage.completion_tokens += result.usage.completion_tokens
            usage.total_tokens += result.usage.total_tokens

    if is_async:

        @functools.wraps(method)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            result: _WithUsage = await method(*args, **kwargs)
            update_usage(result)
            return result

        return async_wrapper
    else:

        @functools.wraps(method)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result: _WithUsage = method(*args, **kwargs)
            update_usage(result)
            return result

        return sync_wrapper


def _openai_api_list() -> Generator[Tuple[Any, Callable, bool], None, None]:
    """Load the list of OpenAI API classes and their corresponding method names."""

    apis: Sequence[Tuple[str, str, str, bool]] = [
        ("openai.resources.chat", "Completions", "create", False),
        ("openai.resources.chat", "AsyncCompletions", "create", True),
        ("openai.resources", "Completions", "create", False),
        ("openai.resources", "AsyncCompletions", "create", True),
        ("openai.resources", "Embeddings", "create", False),
        ("openai.resources", "AsyncEmbeddings", "create", True),
        ("openai.resources", "Responses", "create", False),
        ("openai.resources", "AsyncResponses", "create", True),
    ]

    for module_name, class_name, method_name, is_async in apis:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name, None)
            if cls is None:
                continue
            method = getattr(cls, method_name, None)
            if method is None:
                continue
            yield cls, method, is_async
        except ImportError:
            raise MissingRequiredPackage("Please install the 'openai' package to use the Azure AI Evaluation SDK")
        except AttributeError:
            logging.warning("The module '%s' does not have class '%s' or method '%s'", module_name, class_name, method_name)


def inject_openai_api():
    """This function modifies the create methods of the OpenAI API classes to inject logic
    to enable us to collect token usage data.
    """
    for cls, method, is_async in _openai_api_list():
        # Check if the create method of the openai_api class has already been modified
        if not hasattr(method, KEY_ATTR_ORIGINAL):
            wrapper_method: Callable = _wrap_openai_api_method(method, is_async)
            setattr(wrapper_method, KEY_ATTR_ORIGINAL, method)
            setattr(cls, method.__name__, wrapper_method)


def recover_openai_api():
    """This function restores the original create methods of the OpenAI API classes
    by assigning them back from the _original attributes of the modified methods.
    """
    for cls, method, _ in _openai_api_list():
        if hasattr(method, KEY_ATTR_ORIGINAL):
            original_method = getattr(method, KEY_ATTR_ORIGINAL)
            setattr(cls, method.__name__, original_method)


class CaptureOpenAITokenUsage:
    """Context manager to capture OpenAI token usage."""
    def __init__(self):
        self._tokens = TokenMetrics(0, 0, 0)

    def __enter__(self) -> TokenMetrics:
        _token_metrics.set(TokenMetrics(0, 0, 0))
        return self._tokens

    def __exit__(self, exc_type: Optional[Exception], exc_value: Optional[Exception], traceback: Optional[Any]) -> None:
        captured_metrics = _token_metrics.get()
        self._tokens.update(captured_metrics)