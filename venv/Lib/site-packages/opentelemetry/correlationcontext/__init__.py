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

import typing

from opentelemetry.context import get_value, set_value
from opentelemetry.context.context import Context

_CORRELATION_CONTEXT_KEY = "correlation-context"


def get_correlations(
    context: typing.Optional[Context] = None,
) -> typing.Dict[str, object]:
    """Returns the name/value pairs in the CorrelationContext

    Args:
        context: The Context to use. If not set, uses current Context

    Returns:
        Name/value pairs in the CorrelationContext
    """
    correlations = get_value(_CORRELATION_CONTEXT_KEY, context=context)
    if isinstance(correlations, dict):
        return correlations.copy()
    return {}


def get_correlation(
    name: str, context: typing.Optional[Context] = None
) -> typing.Optional[object]:
    """Provides access to the value for a name/value pair in the
    CorrelationContext

    Args:
        name: The name of the value to retrieve
        context: The Context to use. If not set, uses current Context

    Returns:
        The value associated with the given name, or null if the given name is
        not present.
    """
    return get_correlations(context=context).get(name)


def set_correlation(
    name: str, value: object, context: typing.Optional[Context] = None
) -> Context:
    """Sets a value in the CorrelationContext

    Args:
        name: The name of the value to set
        value: The value to set
        context: The Context to use. If not set, uses current Context

    Returns:
        A Context with the value updated
    """
    correlations = get_correlations(context=context)
    correlations[name] = value
    return set_value(_CORRELATION_CONTEXT_KEY, correlations, context=context)


def remove_correlation(
    name: str, context: typing.Optional[Context] = None
) -> Context:
    """Removes a value from the CorrelationContext

    Args:
        name: The name of the value to remove
        context: The Context to use. If not set, uses current Context

    Returns:
        A Context with the name/value removed
    """
    correlations = get_correlations(context=context)
    correlations.pop(name, None)

    return set_value(_CORRELATION_CONTEXT_KEY, correlations, context=context)


def clear_correlations(context: typing.Optional[Context] = None) -> Context:
    """Removes all values from the CorrelationContext

    Args:
        context: The Context to use. If not set, uses current Context

    Returns:
        A Context with all correlations removed
    """
    return set_value(_CORRELATION_CONTEXT_KEY, {}, context=context)
