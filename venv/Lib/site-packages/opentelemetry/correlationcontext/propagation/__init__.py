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
#
import typing
import urllib.parse

from opentelemetry import correlationcontext
from opentelemetry.context import get_current
from opentelemetry.context.context import Context
from opentelemetry.trace.propagation import httptextformat


class CorrelationContextPropagator(httptextformat.HTTPTextFormat):
    MAX_HEADER_LENGTH = 8192
    MAX_PAIR_LENGTH = 4096
    MAX_PAIRS = 180
    _CORRELATION_CONTEXT_HEADER_NAME = "otcorrelationcontext"

    def extract(
        self,
        get_from_carrier: httptextformat.Getter[
            httptextformat.HTTPTextFormatT
        ],
        carrier: httptextformat.HTTPTextFormatT,
        context: typing.Optional[Context] = None,
    ) -> Context:
        """Extract CorrelationContext from the carrier.

        See
        `opentelemetry.trace.propagation.httptextformat.HTTPTextFormat.extract`
        """

        if context is None:
            context = get_current()

        header = _extract_first_element(
            get_from_carrier(carrier, self._CORRELATION_CONTEXT_HEADER_NAME)
        )

        if not header or len(header) > self.MAX_HEADER_LENGTH:
            return context

        correlations = header.split(",")
        total_correlations = self.MAX_PAIRS
        for correlation in correlations:
            if total_correlations <= 0:
                return context
            total_correlations -= 1
            if len(correlation) > self.MAX_PAIR_LENGTH:
                continue
            try:
                name, value = correlation.split("=", 1)
            except Exception:  # pylint: disable=broad-except
                continue
            context = correlationcontext.set_correlation(
                urllib.parse.unquote(name).strip(),
                urllib.parse.unquote(value).strip(),
                context=context,
            )

        return context

    def inject(
        self,
        set_in_carrier: httptextformat.Setter[httptextformat.HTTPTextFormatT],
        carrier: httptextformat.HTTPTextFormatT,
        context: typing.Optional[Context] = None,
    ) -> None:
        """Injects CorrelationContext into the carrier.

        See
        `opentelemetry.trace.propagation.httptextformat.HTTPTextFormat.inject`
        """
        correlations = correlationcontext.get_correlations(context=context)
        if not correlations:
            return

        correlation_context_string = _format_correlations(correlations)
        set_in_carrier(
            carrier,
            self._CORRELATION_CONTEXT_HEADER_NAME,
            correlation_context_string,
        )


def _format_correlations(correlations: typing.Dict[str, object]) -> str:
    return ",".join(
        key + "=" + urllib.parse.quote_plus(str(value))
        for key, value in correlations.items()
    )


def _extract_first_element(
    items: typing.Iterable[httptextformat.HTTPTextFormatT],
) -> typing.Optional[httptextformat.HTTPTextFormatT]:
    if items is None:
        return None
    return next(iter(items), None)
