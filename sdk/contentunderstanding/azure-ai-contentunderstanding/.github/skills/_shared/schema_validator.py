"""Pure-Python validator for Content Understanding analyzer schema JSON.

Catches structural mistakes (missing keys, unknown ``baseAnalyzerId`` values,
malformed ``contentCategories`` routes) **before** any call to the Content
Understanding service. Failing fast here gives users an actionable error
message and avoids a wasted service round-trip.

Design rules (see ``README.md`` in this directory):

* No ``azure.*`` imports.
* No network calls.
* Standard library only.

The validator accepts either a parsed ``dict`` (preferred) or a path to a
JSON file (convenience).

Public surface:

* :func:`validate_schema` — validate a parsed schema dict.
* :func:`validate_schema_file` — convenience wrapper that loads a JSON file.
* :data:`KNOWN_BASE_ANALYZER_IDS` — allow-list of ``baseAnalyzerId`` values.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Mapping, Optional, Tuple, Union

#: Valid ``baseAnalyzerId`` values for custom analyzers. Only modality-level
#: prebuilts are accepted by the service for ``baseAnalyzerId``; ``*Search``
#: variants and task-specific prebuilts (``prebuilt-invoice``,
#: ``prebuilt-receipt``) return ``InvalidBaseAnalyzerId`` if used here. See
#: https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/analyzer-reference#baseanalyzerid
KNOWN_BASE_ANALYZER_IDS = frozenset(
    {
        "prebuilt-document",
        "prebuilt-audio",
        "prebuilt-video",
        "prebuilt-image",
    }
)

_ALLOWED_FIELD_TYPES = frozenset(
    {"string", "number", "integer", "boolean", "date", "time", "array", "object"}
)

_ALLOWED_FIELD_METHODS = frozenset({"extract", "generate", "classify"})


def validate_schema(
    schema: Mapping[str, Any],
) -> Tuple[bool, List[str]]:
    """Validate a parsed analyzer schema.

    Parameters
    ----------
    schema:
        The parsed schema (a ``dict`` produced by ``json.load`` or equivalent).

    Returns
    -------
    tuple
        ``(ok, errors)``. ``ok`` is ``True`` when the schema is structurally
        valid. ``errors`` is the list of human-readable error messages
        (empty when ``ok`` is ``True``).
    """

    errors: List[str] = []

    if not isinstance(schema, Mapping):
        return False, ["schema must be a JSON object at the top level"]

    base = schema.get("baseAnalyzerId")
    if base is None:
        errors.append("missing required key: baseAnalyzerId")
    elif not isinstance(base, str):
        errors.append("baseAnalyzerId must be a string")
    elif base not in KNOWN_BASE_ANALYZER_IDS:
        errors.append(
            "unknown baseAnalyzerId: "
            f"{base!r}. Known values: {sorted(KNOWN_BASE_ANALYZER_IDS)}"
        )

    config = schema.get("config")
    if config is not None and not isinstance(config, Mapping):
        errors.append("config, if present, must be an object")
        # Bail out: without a well-typed config we can't tell whether this is
        # a single-type or classify-and-route schema, and falling through
        # would emit a confusing cascade of "missing fieldSchema" errors
        # rooted in the same problem.
        return False, errors

    is_classify_route = (
        isinstance(config, Mapping) and "contentCategories" in config
    )

    if is_classify_route:
        errors.extend(_validate_classify_route(config))
        if "fieldSchema" in schema:
            errors.append(
                "classify-and-route schemas should not declare fieldSchema at "
                "the top level; field extraction belongs in inner analyzers"
            )
    else:
        errors.extend(_validate_single_type(schema))

    return (not errors), errors


def validate_schema_file(path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """Validate a schema stored in a JSON file.

    Loads the file, then delegates to :func:`validate_schema`.

    Returns the same ``(ok, errors)`` tuple as :func:`validate_schema`.
    """

    p = Path(path)
    try:
        with p.open("r", encoding="utf-8") as fp:
            schema = json.load(fp)
    except FileNotFoundError:
        return False, [f"schema file not found: {p}"]
    except json.JSONDecodeError as exc:
        return False, [f"schema file is not valid JSON ({p}): {exc.msg} at line {exc.lineno}"]

    return validate_schema(schema)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_single_type(schema: Mapping[str, Any]) -> List[str]:
    """Validate a single-doc-type extraction schema."""

    errors: List[str] = []

    field_schema = schema.get("fieldSchema")
    if field_schema is None:
        errors.append(
            "missing required key: fieldSchema "
            "(single-type schemas must declare fields to extract)"
        )
        return errors

    if not isinstance(field_schema, Mapping):
        errors.append("fieldSchema must be an object")
        return errors

    fields = field_schema.get("fields")
    if fields is None:
        errors.append("fieldSchema.fields is required")
        return errors

    if not isinstance(fields, Mapping):
        errors.append("fieldSchema.fields must be an object mapping field names to definitions")
        return errors

    if not fields:
        errors.append("fieldSchema.fields must declare at least one field")

    for name, definition in fields.items():
        errors.extend(_validate_field_definition(name, definition))

    return errors


def _validate_field_definition(
    name: str, definition: Any, *, path: Optional[str] = None
) -> List[str]:
    errors: List[str] = []
    prefix = path or f"fieldSchema.fields[{name!r}]"

    if not isinstance(definition, Mapping):
        return [f"{prefix} must be an object"]

    field_type = definition.get("type")
    if field_type is None:
        errors.append(f"{prefix}.type is required")
    elif field_type not in _ALLOWED_FIELD_TYPES:
        errors.append(
            f"{prefix}.type {field_type!r} is not one of {sorted(_ALLOWED_FIELD_TYPES)}"
        )

    method = definition.get("method")
    if method is not None and method not in _ALLOWED_FIELD_METHODS:
        errors.append(
            f"{prefix}.method {method!r} is not one of {sorted(_ALLOWED_FIELD_METHODS)}"
        )

    description = definition.get("description")
    if description is not None and not isinstance(description, str):
        errors.append(f"{prefix}.description must be a string")

    # Recurse into nested object/array shapes so typos in child fields are
    # caught here instead of at the service round-trip.
    if field_type == "object":
        props = definition.get("properties")
        if props is not None:
            if not isinstance(props, Mapping):
                errors.append(f"{prefix}.properties must be an object")
            else:
                for child, child_def in props.items():
                    errors.extend(
                        _validate_field_definition(
                            child, child_def, path=f"{prefix}.properties[{child!r}]"
                        )
                    )
    elif field_type == "array":
        items = definition.get("items")
        if items is not None:
            if not isinstance(items, Mapping):
                errors.append(f"{prefix}.items must be an object")
            else:
                errors.extend(
                    _validate_field_definition(
                        "items", items, path=f"{prefix}.items"
                    )
                )

    return errors


def _validate_classify_route(config: Mapping[str, Any]) -> List[str]:
    """Validate the classify-and-route portion of a schema."""

    errors: List[str] = []

    enable_segment = config.get("enableSegment")
    if enable_segment is not True:
        errors.append(
            "classify-and-route schemas must set config.enableSegment = true"
        )

    categories = config.get("contentCategories")
    if not isinstance(categories, Mapping):
        errors.append("config.contentCategories must be an object")
        return errors

    if not categories:
        errors.append("config.contentCategories must declare at least one category")
        return errors

    for name, entry in categories.items():
        prefix = f"config.contentCategories[{name!r}]"
        if not isinstance(entry, Mapping):
            errors.append(f"{prefix} must be an object")
            continue

        description = entry.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{prefix}.description is required and must be a non-empty string")

        analyzer_id = entry.get("analyzerId")
        if analyzer_id is not None and not isinstance(analyzer_id, str):
            errors.append(f"{prefix}.analyzerId, if present, must be a string")

    return errors
