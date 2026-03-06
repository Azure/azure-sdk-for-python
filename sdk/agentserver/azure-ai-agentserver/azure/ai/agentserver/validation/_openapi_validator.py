# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#
# Why not use openapi-spec-validator / openapi-schema-validator / openapi-core?
#
#   - openapi-spec-validator validates that an OpenAPI *document* is well-formed
#     (meta-validation). It does not validate request/response data.
#
#   - openapi-schema-validator (OAS30Validator) handles nullable, readOnly/
#     writeOnly, and OpenAPI keyword stripping natively, but does NOT provide:
#       * $ref resolution from the full spec into extracted sub-schemas,
#       * discriminator-aware oneOf/anyOf error collection (ported from the
#         server-side C# JsonSchemaValidator),
#       * JSON-path-prefixed error messages.
#     Adopting it would save ~65 lines of preprocessing but adds three
#     transitive dependencies (jsonschema-specifications, rfc3339-validator,
#     jsonschema-path) while still requiring all custom error-collection code.
#
#   - openapi-core is a full request/response middleware framework with its
#     own routing and parsing. It conflicts with our Starlette middleware
#     approach and is a much heavier dependency.
#
# Keeping only jsonschema as the single validation dependency gives us full
# control over error output and avoids unnecessary transitive packages.
#
import copy
import json
import logging
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional

import jsonschema
from jsonschema import FormatChecker, ValidationError

logger = logging.getLogger("azure.ai.agentserver")

# ---------------------------------------------------------------------------
# Stdlib-only format checkers so we never depend on optional jsonschema extras
# (rfc3339-validator, fqdn, …).  Registered on a module-level instance that
# is reused for every validation call.
# ---------------------------------------------------------------------------
_format_checker = FormatChecker(formats=())  # start with no built-in checks

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@_format_checker.checks("date-time", raises=ValueError)
def _check_datetime(value: object) -> bool:
    """Validate RFC 3339 / ISO 8601 date-time strings using stdlib only."""
    if not isinstance(value, str):
        return True  # non-string is not a format error
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    datetime.fromisoformat(normalized)
    return True


@_format_checker.checks("date", raises=ValueError)
def _check_date(value: object) -> bool:
    """Validate ISO 8601 date strings (YYYY-MM-DD)."""
    if not isinstance(value, str):
        return True
    datetime.strptime(value, "%Y-%m-%d")
    return True


@_format_checker.checks("email", raises=ValueError)
def _check_email(value: object) -> bool:
    """Basic RFC 5322 email format check (no DNS lookup)."""
    if not isinstance(value, str):
        return True
    if not _EMAIL_RE.match(value):
        raise ValueError(f"Invalid email: {value!r}")
    return True

# OpenAPI keywords that are not part of JSON Schema and must be stripped
# before handing a schema to a JSON Schema validator.
_OPENAPI_ONLY_KEYWORDS: frozenset[str] = frozenset(
    {"discriminator", "xml", "externalDocs", "example"}
)


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
        self._request_body_required = self._is_request_body_required(spec, path)
        raw_request = self._extract_request_schema(spec, path)
        raw_response = self._extract_response_schema(spec, path)
        self._request_schema = (
            self._preprocess_schema(raw_request, context="request")
            if raw_request
            else None
        )
        self._response_schema = (
            self._preprocess_schema(raw_response, context="response")
            if raw_response
            else None
        )

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
        # If requestBody.required is false, allow empty bodies
        if not self._request_body_required and body.strip() == b"":
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

        Uses discriminator-aware error collection for ``oneOf`` / ``anyOf``
        schemas: when a discriminator property is detected across branches the
        validator selects the matching branch and reports only *its* errors,
        avoiding the noisy dump of every branch.

        Error messages are prefixed with the JSON-path of the failing element
        (e.g. ``$.items[0].type: ...``) so callers can pinpoint the problem.

        :param body: Raw bytes to validate.
        :type body: bytes
        :param content_type: The Content-Type header value.
        :type content_type: str
        :param schema: JSON Schema dict to validate against.
        :type schema: dict[str, Any]
        :return: List of validation error strings.  Empty when valid.
        :rtype: list[str]
        """
        if "json" not in content_type.lower():
            return []  # skip validation for non-JSON payloads

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return [f"Invalid JSON body: {exc}"]

        errors: list[str] = []
        validator = jsonschema.Draft7Validator(
            schema, format_checker=_format_checker
        )
        for error in validator.iter_errors(data):
            errors.extend(_collect_errors(error))
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

    @staticmethod
    def _is_request_body_required(spec: dict[str, Any], path: str) -> bool:
        """Check whether ``requestBody.required`` is true for the POST operation.

        :param spec: OpenAPI spec dictionary.
        :type spec: dict[str, Any]
        :param path: The API path (e.g. ``/invocations``).
        :type path: str
        :return: True if the request body is explicitly required (default True).
        :rtype: bool
        """
        paths = spec.get("paths", {})
        operation = paths.get(path, {}).get("post", {})
        request_body = operation.get("requestBody", {})
        return request_body.get("required", True)

    @staticmethod
    def _preprocess_schema(
        schema: dict[str, Any], context: str = "request"
    ) -> dict[str, Any]:
        """Convert OpenAPI-specific keywords into pure JSON Schema.

        Performs a deep copy then applies the following transformations:
        1. ``nullable: true`` → ``type: [originalType, "null"]``
        2. Strip ``readOnly`` properties in request context,
           ``writeOnly`` in response context.
        3. Remove OpenAPI-only keywords (``discriminator``, ``xml``, etc.).

        :param schema: Resolved JSON Schema dict (may contain OpenAPI extensions).
        :type schema: dict[str, Any]
        :param context: Either ``"request"`` or ``"response"``.
        :type context: str
        :return: A pure JSON Schema dict safe for ``jsonschema`` validation.
        :rtype: dict[str, Any]
        """
        schema = copy.deepcopy(schema)
        OpenApiValidator._apply_nullable(schema)
        OpenApiValidator._strip_readonly_writeonly(schema, context)
        OpenApiValidator._strip_openapi_keywords(schema)
        return schema

    @staticmethod
    def _apply_nullable(schema: dict[str, Any]) -> None:
        """Convert ``nullable: true`` to JSON Schema union type in-place.

        Walks the schema tree and transforms
        ``{"type": "string", "nullable": true}`` into
        ``{"type": ["string", "null"]}``.

        :param schema: Schema dict to mutate in-place.
        :type schema: dict[str, Any]
        """
        if not isinstance(schema, dict):
            return
        if schema.pop("nullable", False):
            original = schema.get("type")
            if isinstance(original, str):
                schema["type"] = [original, "null"]
            elif isinstance(original, list) and "null" not in original:
                schema["type"] = original + ["null"]
        # Recurse into nested structures
        for key in ("items", "additionalProperties"):
            child = schema.get(key)
            if isinstance(child, dict):
                OpenApiValidator._apply_nullable(child)
        for prop in schema.get("properties", {}).values():
            if isinstance(prop, dict):
                OpenApiValidator._apply_nullable(prop)
        for keyword in ("allOf", "oneOf", "anyOf"):
            for sub in schema.get(keyword, []):
                if isinstance(sub, dict):
                    OpenApiValidator._apply_nullable(sub)

    @staticmethod
    def _strip_readonly_writeonly(
        schema: dict[str, Any], context: str
    ) -> None:
        """Remove readOnly/writeOnly properties based on context.

        In **request** context, properties marked ``readOnly: true`` are removed
        from ``properties`` and from the ``required`` list (the server generates
        them; clients should not send them).

        In **response** context, ``writeOnly: true`` properties are removed
        (e.g. passwords that the client sends but the server never echoes back).

        :param schema: Schema dict to mutate in-place.
        :type schema: dict[str, Any]
        :param context: ``"request"`` or ``"response"``.
        :type context: str
        """
        if not isinstance(schema, dict):
            return
        props = schema.get("properties", {})
        required = schema.get("required", [])
        to_remove: list[str] = []
        for name, prop_schema in props.items():
            if not isinstance(prop_schema, dict):
                continue
            if context == "request" and prop_schema.get("readOnly"):
                to_remove.append(name)
            elif context == "response" and prop_schema.get("writeOnly"):
                to_remove.append(name)
        for name in to_remove:
            props.pop(name, None)
            if name in required:
                required.remove(name)
        # Recurse into nested objects
        for prop in props.values():
            if isinstance(prop, dict):
                OpenApiValidator._strip_readonly_writeonly(prop, context)
        child = schema.get("items")
        if isinstance(child, dict):
            OpenApiValidator._strip_readonly_writeonly(child, context)
        for keyword in ("allOf", "oneOf", "anyOf"):
            for sub in schema.get(keyword, []):
                if isinstance(sub, dict):
                    OpenApiValidator._strip_readonly_writeonly(sub, context)

    @staticmethod
    def _strip_openapi_keywords(schema: dict[str, Any]) -> None:
        """Remove OpenAPI-only keywords that confuse JSON Schema validators.

        Strips ``discriminator``, ``xml``, ``externalDocs``, and ``example``
        from the schema tree in-place.

        :param schema: Schema dict to mutate in-place.
        :type schema: dict[str, Any]
        """
        if not isinstance(schema, dict):
            return
        for kw in _OPENAPI_ONLY_KEYWORDS:
            schema.pop(kw, None)
        for key in ("items", "additionalProperties"):
            child = schema.get(key)
            if isinstance(child, dict):
                OpenApiValidator._strip_openapi_keywords(child)
        for prop in schema.get("properties", {}).values():
            if isinstance(prop, dict):
                OpenApiValidator._strip_openapi_keywords(prop)
        for keyword in ("allOf", "oneOf", "anyOf"):
            for sub in schema.get(keyword, []):
                if isinstance(sub, dict):
                    OpenApiValidator._strip_openapi_keywords(sub)


# ------------------------------------------------------------------
# Discriminator-aware error collection helpers
# ------------------------------------------------------------------


def _format_error(error: ValidationError) -> str:
    """Format a single validation error with its JSON path prefix.

    :param error: A ``jsonschema`` validation error.
    :type error: ValidationError
    :return: Human-readable error string, optionally path-prefixed.
    :rtype: str
    """
    path = error.json_path
    if path and path != "$":
        return f"{path}: {error.message}"
    return error.message


def _collect_errors(error: ValidationError) -> list[str]:
    """Collect formatted error messages from a ``ValidationError``.

    For ``oneOf`` / ``anyOf`` errors the helper attempts discriminator-aware
    branch selection (mirroring the server-side C# ``JsonSchemaValidator``).
    When a discriminator property is detected, only the *matching* branch's
    errors are reported, avoiding a noisy dump of every branch.

    :param error: A ``jsonschema`` validation error.
    :type error: ValidationError
    :return: List of formatted error strings.
    :rtype: list[str]
    """
    if error.validator in ("oneOf", "anyOf") and error.context:
        return _collect_composition_errors(error)
    return [_format_error(error)]


def _collect_composition_errors(error: ValidationError) -> list[str]:
    """Handle ``oneOf`` / ``anyOf`` errors with discriminator-based branch selection.

    Algorithm (ported from the C# ``JsonSchemaValidator``):

    1. Group errors by branch index (``schema_path[0]``).
    2. Detect a *discriminator path*: a ``const`` / ``type`` / ``enum``
       error that appears at the same ``absolute_path`` in the majority of
       branches (threshold: ``max(2, ceil(n/2))``).
    3. The *matching branch* is the one **without** a discriminator error
       at that path.
    4. Report only the matching branch's errors.  If no branch matches,
       report a concise ``"Invalid value. Expected one of: ..."`` message.

    Falls back to ``best_match`` when no discriminator can be identified.

    :param error: A ``oneOf`` / ``anyOf`` validation error.
    :type error: ValidationError
    :return: List of formatted error strings.
    :rtype: list[str]
    """
    # Group sub-errors by branch index (first element of schema_path)
    branch_groups: dict[int, list[ValidationError]] = {}
    for sub in error.context:
        if sub.schema_path:
            idx = sub.schema_path[0]
            if isinstance(idx, int):
                branch_groups.setdefault(idx, []).append(sub)

    if len(branch_groups) < 2:
        # Cannot do branch analysis — fallback
        best = jsonschema.exceptions.best_match([error])
        if best is not None and best is not error:
            return _collect_errors(best)
        return [_format_error(error)]

    disc_path = _find_discriminator_path(branch_groups)

    if disc_path is None:
        best = jsonschema.exceptions.best_match([error])
        if best is not None and best is not error:
            return _collect_errors(best)
        return [_format_error(error)]

    # Find the branch that matches the discriminator value
    matching_idx = _find_matching_branch(branch_groups, disc_path)

    if matching_idx is not None:
        result: list[str] = []
        for sub in branch_groups[matching_idx]:
            result.extend(_collect_errors(sub))
        return result if result else [_format_error(error)]

    # No matching branch — report the discriminator mismatch
    return _report_discriminator_error(branch_groups, disc_path, error)


_DISCRIMINATOR_VALIDATORS: frozenset[str] = frozenset({"const", "type", "enum"})


def _find_discriminator_path(
    branch_groups: dict[int, list[ValidationError]],
) -> Optional[tuple[str | int, ...]]:
    """Detect a discriminator property across ``oneOf`` / ``anyOf`` branches.

    A discriminator is a property whose ``const``, ``enum``, or ``type``
    constraint fails at the same ``absolute_path`` in the majority of
    branches.

    :param branch_groups: Errors grouped by branch index.
    :type branch_groups: dict[int, list[ValidationError]]
    :return: The ``absolute_path`` of the discriminator as a tuple, or *None*.
    :rtype: Optional[tuple[str | int, ...]]
    """
    n_branches = len(branch_groups)
    if n_branches < 2:
        return None

    # Collect discriminator-error paths per branch
    per_branch_paths: list[set[tuple[str | int, ...]]] = []
    for errors in branch_groups.values():
        paths: set[tuple[str | int, ...]] = set()
        for err in errors:
            if err.validator in _DISCRIMINATOR_VALIDATORS:
                paths.add(tuple(err.absolute_path))
        per_branch_paths.append(paths)

    path_counts: Counter[tuple[str | int, ...]] = Counter()
    for paths in per_branch_paths:
        for p in paths:
            path_counts[p] += 1

    min_threshold = (n_branches + 1) // 2  # ceil(n/2) — at least half the branches
    for path, count in path_counts.most_common():
        if count >= min_threshold:
            return path
    return None


def _find_matching_branch(
    branch_groups: dict[int, list[ValidationError]],
    disc_path: tuple[str | int, ...],
) -> Optional[int]:
    """Return the branch index that has **no** discriminator error at *disc_path*.

    :param branch_groups: Errors grouped by branch index.
    :type branch_groups: dict[int, list[ValidationError]]
    :param disc_path: The discriminator property path.
    :type disc_path: tuple[str | int, ...]
    :return: The matching branch index or *None*.
    :rtype: Optional[int]
    """
    for idx, errors in branch_groups.items():
        has_disc_error = any(
            err.validator in _DISCRIMINATOR_VALIDATORS
            and tuple(err.absolute_path) == disc_path
            for err in errors
        )
        if not has_disc_error:
            return idx
    return None


def _report_discriminator_error(
    branch_groups: dict[int, list[ValidationError]],
    disc_path: tuple[str | int, ...],
    parent: ValidationError,
) -> list[str]:
    """Produce a concise discriminator-mismatch message.

    Collects all expected ``const`` / ``enum`` values from the branches and
    reports them as ``"Invalid value. Expected one of: X, Y, Z"``.

    :param branch_groups: Errors grouped by branch index.
    :type branch_groups: dict[int, list[ValidationError]]
    :param disc_path: The discriminator property path.
    :type disc_path: tuple[str | int, ...]
    :param parent: The parent ``oneOf`` / ``anyOf`` error.
    :type parent: ValidationError
    :return: List containing a single formatted error string.
    :rtype: list[str]
    """
    # Build the JSON-path string for the discriminator property
    path_str = "$"
    for segment in disc_path:
        if isinstance(segment, int):
            path_str += f"[{segment}]"
        else:
            path_str += f".{segment}"

    # Check for type errors first (more fundamental than const/enum)
    for errors in branch_groups.values():
        for err in errors:
            if err.validator == "type" and tuple(err.absolute_path) == disc_path:
                return [f"{path_str}: {err.message}"]

    # Collect expected values from const and enum errors
    expected: list[str] = []
    for errors in branch_groups.values():
        for err in errors:
            if tuple(err.absolute_path) != disc_path:
                continue
            if err.validator == "const":
                val = err.schema.get("const") if isinstance(err.schema, dict) else None
                if val is not None:
                    formatted = json.dumps(val) if not isinstance(val, str) else f'"{val}"'
                    if formatted not in expected:
                        expected.append(formatted)
            elif err.validator == "enum":
                enum_vals = err.schema.get("enum", []) if isinstance(err.schema, dict) else []
                for val in enum_vals:
                    formatted = json.dumps(val) if not isinstance(val, str) else f'"{val}"'
                    if formatted not in expected:
                        expected.append(formatted)

    if expected:
        if len(expected) == 1:
            return [f"{path_str}: Invalid value. Expected: {expected[0]}"]
        return [f"{path_str}: Invalid value. Expected one of: {', '.join(expected)}"]

    # Fallback
    return [_format_error(parent)]


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
            # Preserve sibling keywords (e.g. nullable: true alongside $ref)
            siblings = {k: v for k, v in node.items() if k != "$ref"}
            resolved = _resolve_refs_deep(spec, resolved, _seen)
            if siblings and isinstance(resolved, dict):
                merged = dict(resolved)
                merged.update(siblings)
                return merged
            return resolved
        return {k: _resolve_refs_deep(spec, v, _seen) for k, v in node.items()}

    if isinstance(node, list):
        return [_resolve_refs_deep(spec, item, _seen) for item in node]

    return node
