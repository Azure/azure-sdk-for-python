# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
from typing import Any, Optional

import jsonschema

logger = logging.getLogger("azure.ai.agentserver")


class OpenApiValidator:
    """Validates request/response bodies against an OpenAPI spec.

    Extracts the request and response JSON schemas from the provided OpenAPI spec dict
    and uses ``jsonschema`` to validate bodies at runtime.

    :param spec: An OpenAPI spec dictionary.
    :type spec: dict[str, Any]
    """

    def __init__(self, spec: dict[str, Any], path: str = "/invocations") -> None:
        self._spec = spec
        self._path = path
        self._request_schema = self._extract_request_schema(spec, path)
        self._response_schema = self._extract_response_schema(spec, path)

    def validate_request(self, body: bytes, content_type: str) -> list[str]:
        """Validate a request body against the spec's request schema.

        :param body: Raw request body bytes.
        :type body: bytes
        :param content_type: The Content-Type header value.
        :type content_type: str
        :return: List of validation error messages. Empty when valid.
        :rtype: list[str]
        """
        if self._request_schema is None:
            return []
        return self._validate_body(body, content_type, self._request_schema)

    def validate_response(self, body: bytes, content_type: str) -> list[str]:
        """Validate a response body against the spec's response schema.

        :param body: Raw response body bytes.
        :type body: bytes
        :param content_type: The Content-Type header value.
        :type content_type: str
        :return: List of validation error messages. Empty when valid.
        :rtype: list[str]
        """
        if self._response_schema is None:
            return []
        return self._validate_body(body, content_type, self._response_schema)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_body(body: bytes, content_type: str, schema: dict[str, Any]) -> list[str]:
        """Parse body as JSON and validate against *schema*.

        :param body: Raw bytes to validate.
        :type body: bytes
        :param content_type: The Content-Type header value.
        :type content_type: str
        :param schema: JSON Schema dict to validate against.
        :type schema: dict[str, Any]
        :return: List of validation error strings.
        :rtype: list[str]
        """
        if "json" not in content_type.lower():
            return []  # skip validation for non-JSON payloads

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return [f"Invalid JSON body: {exc}"]

        errors: list[str] = []
        validator = jsonschema.Draft7Validator(schema)
        for error in validator.iter_errors(data):
            errors.append(error.message)
        return errors

    @staticmethod
    def _extract_request_schema(spec: dict[str, Any], path: str) -> Optional[dict[str, Any]]:
        """Extract the request body JSON schema from the POST operation at *path*.

        :param spec: OpenAPI spec dictionary.
        :type spec: dict[str, Any]
        :param path: The API path (e.g. ``/invocations``).
        :type path: str
        :return: JSON Schema dict or None.
        :rtype: Optional[dict[str, Any]]
        """
        return OpenApiValidator._find_schema_in_paths(
            spec, path, "post", "requestBody"
        )

    @staticmethod
    def _extract_response_schema(spec: dict[str, Any], path: str) -> Optional[dict[str, Any]]:
        """Extract the response body JSON schema from the POST operation at *path*.

        :param spec: OpenAPI spec dictionary.
        :type spec: dict[str, Any]
        :param path: The API path (e.g. ``/invocations``).
        :type path: str
        :return: JSON Schema dict or None.
        :rtype: Optional[dict[str, Any]]
        """
        return OpenApiValidator._find_schema_in_paths(
            spec, path, "post", "responses"
        )

    @staticmethod
    def _find_schema_in_paths(
        spec: dict[str, Any],
        path: str,
        method: str,
        section: str,
    ) -> Optional[dict[str, Any]]:
        """Walk the spec to find a JSON schema for the given path/method/section.

        :param spec: OpenAPI spec dictionary.
        :type spec: dict[str, Any]
        :param path: The API path (e.g. ``/invocations``).
        :type path: str
        :param method: HTTP method (e.g. ``post``).
        :type method: str
        :param section: Either ``requestBody`` or ``responses``.
        :type section: str
        :return: Resolved JSON Schema dict or None.
        :rtype: Optional[dict[str, Any]]
        """
        paths = spec.get("paths", {})
        operation = paths.get(path, {}).get(method, {})

        if section == "requestBody":
            request_body = operation.get("requestBody", {})
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema")
            return _resolve_refs_deep(spec, schema) if schema else None

        if section == "responses":
            responses = operation.get("responses", {})
            # Try 200, then 201, then first available
            for code in ("200", "201"):
                resp = responses.get(code, {})
                content = resp.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema")
                if schema:
                    return _resolve_refs_deep(spec, schema)
            # Fallback: first response with JSON content
            for resp in responses.values():
                if isinstance(resp, dict):
                    content = resp.get("content", {})
                    json_content = content.get("application/json", {})
                    schema = json_content.get("schema")
                    if schema:
                        return _resolve_refs_deep(spec, schema)
        return None


def _resolve_ref(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Resolve a single ``$ref`` pointer within the spec.

    :param spec: The full OpenAPI spec dictionary.
    :type spec: dict[str, Any]
    :param schema: A schema dict that may contain a ``$ref`` key.
    :type schema: dict[str, Any]
    :return: The resolved schema.
    :rtype: dict[str, Any]
    """
    if "$ref" not in schema:
        return schema
    ref_path = schema["$ref"]  # e.g. "#/components/schemas/MyModel"
    parts = ref_path.lstrip("#/").split("/")
    current: Any = spec
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return schema  # can't resolve, return as-is
    return current if isinstance(current, dict) else schema


def _resolve_refs_deep(spec: dict[str, Any], node: Any, _seen: Optional[set[str]] = None) -> Any:
    """Recursively resolve all ``$ref`` pointers in a schema tree.

    Walks the schema, replacing every ``{"$ref": "..."}`` with the referenced
    definition inlined from *spec*.  A *_seen* set guards against infinite
    recursion from circular references.

    :param spec: The full OpenAPI spec dictionary.
    :type spec: dict[str, Any]
    :param node: The current schema node (dict, list, or scalar).
    :type node: Any
    :param _seen: Set of already-visited ``$ref`` paths (cycle guard).
    :type _seen: Optional[set[str]]
    :return: The schema tree with all ``$ref`` pointers inlined.
    :rtype: Any
    """
    if _seen is None:
        _seen = set()

    if isinstance(node, dict):
        if "$ref" in node:
            ref_path = node["$ref"]
            if ref_path in _seen:
                return node  # circular – leave the $ref as-is
            _seen = _seen | {ref_path}
            resolved = _resolve_ref(spec, node)
            if resolved is node:
                return node  # couldn't resolve
            return _resolve_refs_deep(spec, resolved, _seen)
        return {k: _resolve_refs_deep(spec, v, _seen) for k, v in node.items()}

    if isinstance(node, list):
        return [_resolve_refs_deep(spec, item, _seen) for item in node]

    return node
