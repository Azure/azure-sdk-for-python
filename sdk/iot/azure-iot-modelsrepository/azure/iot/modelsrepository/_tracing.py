# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from contextlib import contextmanager
from azure.core.settings import settings
from azure.core.tracing import SpanKind


TRACE_NAMESPACE = "modelsrepository"


@contextmanager
def trace_context_manager(span_name):
    span_impl_type = settings.tracing_implementation()

    if span_impl_type is not None:
        with span_impl_type(name=span_name) as child:
            child.kind = SpanKind.CLIENT
            yield child
    else:
        yield None
