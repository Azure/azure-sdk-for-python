# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urllib.parse
from re import escape, sub
from typing import Dict, Sequence

from wrapt import ObjectProxy

from opentelemetry import context, trace

# pylint: disable=unused-import
# pylint: disable=E0611
from opentelemetry.context import _SUPPRESS_INSTRUMENTATION_KEY  # noqa: F401
from opentelemetry.propagate import extract
from opentelemetry.trace import StatusCode
from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)

propagator = TraceContextTextMapPropagator()


def extract_attributes_from_object(
    obj: any, attributes: Sequence[str], existing: Dict[str, str] = None
) -> Dict[str, str]:
    extracted = {}
    if existing:
        extracted.update(existing)
    for attr in attributes:
        value = getattr(obj, attr, None)
        if value is not None:
            extracted[attr] = str(value)
    return extracted


def http_status_to_status_code(
    status: int,
    allow_redirect: bool = True,
    server_span: bool = False,
) -> StatusCode:
    """Converts an HTTP status code to an OpenTelemetry canonical status code

    Args:
        status (int): HTTP status code
    """
    # See: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/http.md#status
    if not isinstance(status, int):
        return StatusCode.UNSET

    if status < 100:
        return StatusCode.ERROR
    if status <= 299:
        return StatusCode.UNSET
    if status <= 399 and allow_redirect:
        return StatusCode.UNSET
    if status <= 499 and server_span:
        return StatusCode.UNSET
    return StatusCode.ERROR


def unwrap(obj, attr: str):
    """Given a function that was wrapped by wrapt.wrap_function_wrapper, unwrap it

    Args:
        obj: Object that holds a reference to the wrapped function
        attr (str): Name of the wrapped function
    """
    func = getattr(obj, attr, None)
    if func and isinstance(func, ObjectProxy) and hasattr(func, "__wrapped__"):
        setattr(obj, attr, func.__wrapped__)


def _start_internal_or_server_span(
    tracer,
    span_name,
    start_time,
    context_carrier,
    context_getter,
    attributes=None,
):
    """Returns internal or server span along with the token which can be used by caller to reset context


    Args:
        tracer : tracer in use by given instrumentation library
        span_name (string): name of the span
        start_time : start time of the span
        context_carrier : object which contains values that are
            used to construct a Context. This object
            must be paired with an appropriate getter
            which understands how to extract a value from it.
        context_getter : an object which contains a get function that can retrieve zero
            or more values from the carrier and a keys function that can get all the keys
            from carrier.
    """

    token = ctx = span_kind = None
    if trace.get_current_span() is trace.INVALID_SPAN:
        ctx = extract(context_carrier, getter=context_getter)
        token = context.attach(ctx)
        span_kind = trace.SpanKind.SERVER
    else:
        ctx = context.get_current()
        span_kind = trace.SpanKind.INTERNAL
    span = tracer.start_span(
        name=span_name,
        context=ctx,
        kind=span_kind,
        start_time=start_time,
        attributes=attributes,
    )
    return span, token


def _url_quote(s) -> str:  # pylint: disable=invalid-name
    if not isinstance(s, (str, bytes)):
        return s
    quoted = urllib.parse.quote(s)
    # Since SQL uses '%' as a keyword, '%' is a by-product of url quoting
    # e.g. foo,bar --> foo%2Cbar
    # thus in our quoting, we need to escape it too to finally give
    #      foo,bar --> foo%%2Cbar
    return quoted.replace("%", "%%")


def _get_opentelemetry_values() -> dict:
    """
    Return the OpenTelemetry Trace and Span IDs if Span ID is set in the
    OpenTelemetry execution context.
    """
    # Insert the W3C TraceContext generated
    _headers = {}
    propagator.inject(_headers)
    return _headers


def _python_path_without_directory(python_path, directory, path_separator):
    return sub(
        rf"{escape(directory)}{path_separator}(?!$)",
        "",
        python_path,
    )
