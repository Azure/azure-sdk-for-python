# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
from typing import Dict

from azure.core import CaseInsensitiveEnumMeta  # type: ignore[attr-defined] # pylint: disable=no-name-in-module


class OpenTelemetrySchemaVersion(
    str, Enum, metaclass=CaseInsensitiveEnumMeta
):  # pylint: disable=enum-must-inherit-case-insensitive-enum-meta

    V1_19_0 = "1.19.0"


class OpenTelemetrySchema:

    SUPPORTED_VERSIONS = (OpenTelemetrySchemaVersion.V1_19_0,)

    # Mappings of attributes potentially reported by Azure SDKs to corresponding ones that follow
    # OpenTelemetry semantic conventions.
    _ATTRIBUTE_MAPPINGS = {
        OpenTelemetrySchemaVersion.V1_19_0: {
            "x-ms-client-request-id": "az.client_request_id",
            "x-ms-request-id": "az.service_request_id",
            "http.user_agent": "user_agent.original",
            "message_bus.destination": "messaging.destination.name",
            "peer.address": "net.peer.name",
        }
    }

    @classmethod
    def get_latest_version(cls) -> OpenTelemetrySchemaVersion:
        return OpenTelemetrySchemaVersion(cls.SUPPORTED_VERSIONS[-1])

    @classmethod
    def get_attribute_mappings(cls, version: OpenTelemetrySchemaVersion) -> Dict[str, str]:
        return cls._ATTRIBUTE_MAPPINGS[version]

    @classmethod
    def get_schema_url(cls, version: OpenTelemetrySchemaVersion) -> str:
        return f"https://opentelemetry.io/schemas/{version}"
