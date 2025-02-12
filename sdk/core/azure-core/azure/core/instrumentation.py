# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Optional, Union, Sequence, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from .tracing.opentelemetry import OpenTelemetryTracer
    except ImportError:
        pass


AttributeValue = Union[
    str,
    bool,
    int,
    float,
    Sequence[str],
    Sequence[bool],
    Sequence[int],
    Sequence[float],
]
Attributes = Mapping[str, AttributeValue]


def _get_tracer_impl():
    # Check if OpenTelemetry is available/installed.
    try:
        from .tracing.opentelemetry import OpenTelemetryTracer

        return OpenTelemetryTracer
    except ImportError:
        return None


class Instrumentation:
    """A manager for handling instrumentation providers.

    :keyword library_name: The name of the library to use in the provided instrumentation.
    :paramtype library_name: str
    :keyword library_version: The version of the library to use in the provided instrumentation.
    :paramtype library_version: str
    :keyword schema_url: Specifies the Schema URL of the emitted instrumentation.
    :paramtype schema_url: str
    :keyword attributes: Attributes to add to the emitted instrumentation.
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
        self.library_name = library_name
        self.library_version = library_version
        self.schema_url = schema_url
        self.attributes = attributes

    def get_tracer(self) -> Optional["OpenTelemetryTracer"]:
        """Get the OpenTelemetry tracer instance if available.

        If OpenTelemetry is not available, this method will return None. If the tracer instance has not been created
        yet, it will be created and returned. Otherwise, the existing tracer instance will be returned.

        :return: The OpenTelemetry tracer instance if available.
        :rtype: Optional[~azure.core.tracing.opentelemetry.OpenTelemetryTracer]
        """
        if self._tracer is None:
            tracer_impl = _get_tracer_impl()
            if tracer_impl:
                self._tracer = tracer_impl(
                    library_name=self.library_name,
                    library_version=self.library_version,
                    schema_url=self.schema_url,
                    attributes=self.attributes,
                )
        return self._tracer


default_instrumentation = Instrumentation()
"""The global Instrumentation instance.

:type default_instrumentation: ~azure.core.instrumentation.Instrumentation
"""
