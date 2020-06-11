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
import logging
import typing

from opentelemetry.context.context import Context
from opentelemetry.trace.propagation import httptextformat

logger = logging.getLogger(__name__)


class CompositeHTTPPropagator(httptextformat.HTTPTextFormat):
    """ CompositeHTTPPropagator provides a mechanism for combining multiple
    propagators into a single one.

    Args:
        propagators: the list of propagators to use
    """

    def __init__(
        self, propagators: typing.Sequence[httptextformat.HTTPTextFormat]
    ) -> None:
        self._propagators = propagators

    def extract(
        self,
        get_from_carrier: httptextformat.Getter[
            httptextformat.HTTPTextFormatT
        ],
        carrier: httptextformat.HTTPTextFormatT,
        context: typing.Optional[Context] = None,
    ) -> Context:
        """ Run each of the configured propagators with the given context and carrier.
        Propagators are run in the order they are configured, if multiple
        propagators write the same context key, the propagator later in the list
        will override previous propagators.

        See `opentelemetry.trace.propagation.httptextformat.HTTPTextFormat.extract`
        """
        for propagator in self._propagators:
            context = propagator.extract(get_from_carrier, carrier, context)
        return context  # type: ignore

    def inject(
        self,
        set_in_carrier: httptextformat.Setter[httptextformat.HTTPTextFormatT],
        carrier: httptextformat.HTTPTextFormatT,
        context: typing.Optional[Context] = None,
    ) -> None:
        """ Run each of the configured propagators with the given context and carrier.
        Propagators are run in the order they are configured, if multiple
        propagators write the same carrier key, the propagator later in the list
        will override previous propagators.

        See `opentelemetry.trace.propagation.httptextformat.HTTPTextFormat.inject`
        """
        for propagator in self._propagators:
            propagator.inject(set_in_carrier, carrier, context)
