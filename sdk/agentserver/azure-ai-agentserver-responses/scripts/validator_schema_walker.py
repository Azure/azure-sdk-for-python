# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Schema walking helpers for validator generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def resolve_ref(ref: str) -> str:
    """Extract schema name from OpenAPI $ref values."""
    return ref.rsplit("/", 1)[-1]


def _iter_subschemas(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """Yield nested schema objects that may contain references."""
    nested: list[dict[str, Any]] = []

    for key in ("oneOf", "anyOf", "allOf"):
        branches = schema.get(key, [])
        if isinstance(branches, list):
            nested.extend([branch for branch in branches if isinstance(branch, dict)])

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        nested.extend([value for value in properties.values() if isinstance(value, dict)])

    items = schema.get("items")
    if isinstance(items, dict):
        nested.append(items)

    additional = schema.get("additionalProperties")
    if isinstance(additional, dict):
        nested.append(additional)

    return nested


@dataclass
class SchemaWalker:
    """Collect schemas reachable from one or more roots."""

    schemas: dict[str, dict[str, Any]]
    reachable: dict[str, dict[str, Any]] = field(default_factory=dict)
    _visited: set[str] = field(default_factory=set)

    def walk(self, name: str) -> None:
        """Walk a schema by name and recursively collect reachable references."""
        if name in self._visited:
            return
        self._visited.add(name)

        schema = self.schemas.get(name)
        if schema is None:
            return

        self.reachable[name] = schema
        self._walk_schema(schema)

    def _walk_schema(self, schema: dict[str, Any]) -> None:
        """Walk nested schema branches."""
        ref = schema.get("$ref")
        if isinstance(ref, str):
            self.walk(resolve_ref(ref))
            return

        for nested in _iter_subschemas(schema):
            self._walk_schema(nested)


def discover_post_request_roots(spec: dict[str, Any]) -> list[str]:
    """Discover root schema names referenced by POST request bodies."""
    roots: list[str] = []
    paths = spec.get("paths", {})

    for _path, methods in sorted(paths.items()):
        if not isinstance(methods, dict):
            continue
        post = methods.get("post")
        if not isinstance(post, dict):
            continue
        request_body = post.get("requestBody", {})
        content = request_body.get("content", {}).get("application/json", {})
        schema = content.get("schema", {})

        if isinstance(schema, dict) and isinstance(schema.get("$ref"), str):
            roots.append(resolve_ref(schema["$ref"]))
            continue

        if isinstance(schema, dict):
            for key in ("oneOf", "anyOf"):
                branches = schema.get(key, [])
                if not isinstance(branches, list):
                    continue
                for branch in branches:
                    if isinstance(branch, dict) and isinstance(branch.get("$ref"), str):
                        roots.append(resolve_ref(branch["$ref"]))

    deduped: list[str] = []
    seen: set[str] = set()
    for root in roots:
        if root not in seen:
            seen.add(root)
            deduped.append(root)
    return deduped
