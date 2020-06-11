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
from typing import Optional

from opentelemetry import trace as trace_api
from opentelemetry.context import get_value, set_value
from opentelemetry.context.context import Context

SPAN_KEY = "current-span"


def set_span_in_context(
    span: trace_api.Span, context: Optional[Context] = None
) -> Context:
    ctx = set_value(SPAN_KEY, span, context=context)
    return ctx


def get_span_from_context(context: Optional[Context] = None) -> trace_api.Span:
    span = get_value(SPAN_KEY, context=context)
    if not isinstance(span, trace_api.Span):
        return trace_api.INVALID_SPAN
    return span
