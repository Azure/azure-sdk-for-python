# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Optional, TYPE_CHECKING

from ._models import Attributes

if TYPE_CHECKING:
    try:
        from .opentelemetry_tracer import OpenTelemetryTracer
    except ImportError:
        pass


def _get_tracer_impl():
    # Check if OpenTelemetry is available/installed.
    try:
        from .opentelemetry_tracer import OpenTelemetryTracer

        return OpenTelemetryTracer
    except ImportError:
        return None


class TracerProvider:
    """A manager for a tracer instance.

    :keyword library_name: The name of the library to use in the tracer.
    :paramtype library_name: str
    :keyword library_version: The version of the library to use in the tracer.
    :paramtype library_version: str
    :keyword schema_url: Specifies the Schema URL of the emitted spans.
    :paramtype schema_url: str
    :keyword attributes: Attributes to add to the emitted spans.
    :paramtype attributes: Mapping[str, Any]
    """

    def __init__(
        self,
        *,
        library_name: Optional[str] = None,
        library_version: Optional[str] = None,
        schema_url: Optional[str] = None,
        attributes: Optional[Attributes] = None,
    ) -> None:
        self._tracer = None
        self._library_name = library_name
        self._library_version = library_version
        self._schema_url = schema_url
        self._attributes = attributes

    def get_tracer(self) -> Optional["OpenTelemetryTracer"]:
        """Get the OpenTelemetry tracer instance if available.

        :return: The OpenTelemetry tracer instance if available.
        :rtype: Optional[OpenTelemetryTracer]
        """
        if self._tracer is None:
            tracer_impl = _get_tracer_impl()
            if tracer_impl:
                self._tracer = tracer_impl(
                    library_name=self._library_name,
                    library_version=self._library_version,
                    schema_url=self._schema_url,
                    attributes=self._attributes,
                )
        return self._tracer


default_tracer_provider = TracerProvider()
