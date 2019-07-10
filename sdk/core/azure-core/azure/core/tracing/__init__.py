# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.tracing.abstract_span import AbstractSpan
from azure.core.tracing.context import tracing_context
from azure.core.tracing.decorator import distributed_tracing_decorator

try:
    from azure.core.tracing.decorator_async import distributed_tracing_decorator_async
except ImportError:
    distributed_tracing_decorator_async = lambda x: x

__all__ = [
    "tracing_context",
    "AbstractSpan",
    "distributed_tracing_decorator",
    "distributed_tracing_decorator_async",
]
