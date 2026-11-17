# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Schema walking helpers for validator generation."""

from __future__ import annotations

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

    # Walk discriminator mapping refs so schemas like ItemMessage / FunctionTool
    # that are only reachable via a discriminator are included in the reachable set
    # (and therefore have the overlay applied before the emitter sees them).
    disc = schema.get("discriminator")
    if isinstance(disc, dict):
        mapping = disc.get("mapping", {})
        if isinstance(mapping, dict):
            for ref_str in mapping.values():
                if isinstance(ref_str, str):
                    nested.append({"$ref": ref_str})

    return nested


class SchemaWalker:
    """Collect schemas reachable from one or more roots."""

    def __init__(
        self,
        schemas: dict[str, dict[str, Any]],
        overlay: dict[str, Any] | None = None,
    ) -> None:
        self.schemas = schemas
        self.overlay: dict[str, Any] = overlay or {}
        self.reachable: dict[str, dict[str, Any]] = {}
        self._visited: set[str] = set()

    def walk(self, name: str) -> None:
        """Walk a schema by name and recursively collect reachable references."""
        if name in self._visited:
            return
        self._visited.add(name)

        schema = self.schemas.get(name)
        if schema is None:
            return

        schema = self._apply_overlay(name, dict(schema))
        self.reachable[name] = schema
        self._walk_schema(schema)

    def _apply_overlay(self, name: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Apply overlay fixes to a schema.

        Supports four overlay keys per schema entry:
        - ``required``: replace the required list entirely.
        - ``not_required``: remove individual fields from required and mark their
          property schemas as ``nullable`` so ``None`` is accepted.
        - ``properties``: merge per-property constraint overrides (e.g. minimum/maximum).
        - ``default_discriminator``: set a default discriminator value for the schema's
          discriminator dispatch. When the discriminator property is absent from the
          payload, this value is used instead of rejecting the input.
        """
        overlay_schemas = self.overlay.get("schemas", {})
        # Try exact name first, then fall back to the name with any "Vendor." prefix stripped
        # (e.g. "OpenAI.ItemMessage" -> "ItemMessage") to stay compatible with the overlay
        # format shared with the TypeSpec code generator, where TypeSpec uses bare names.
        overlay_entry = overlay_schemas.get(name)
        if not overlay_entry:
            bare = name.rsplit(".", 1)[-1] if "." in name else None
            if bare:
                overlay_entry = overlay_schemas.get(bare)
        if not overlay_entry:
            return schema

        # Replace required list entirely
        if "required" in overlay_entry:
            schema["required"] = list(overlay_entry["required"])

        # Remove individual fields from required; mark those properties nullable
        if "not_required" in overlay_entry:
            current_required = list(schema.get("required", []))
            for field in overlay_entry["not_required"]:
                if field in current_required:
                    current_required.remove(field)
                # Mark property nullable so the emitter accepts None/absent values
                props = schema.get("properties")
                if isinstance(props, dict) and field in props:
                    props[field] = dict(props[field])
                    props[field]["nullable"] = True
            schema["required"] = current_required

        # Merge property-level constraint overrides
        if "properties" in overlay_entry:
            if "properties" not in schema:
                schema["properties"] = {}
            for prop_name, constraints in overlay_entry["properties"].items():
                if prop_name not in schema["properties"]:
                    schema["properties"][prop_name] = {}
                else:
                    schema["properties"][prop_name] = dict(schema["properties"][prop_name])
                schema["properties"][prop_name].update(constraints)

        # Inject default_discriminator into the schema's discriminator dict
        if "default_discriminator" in overlay_entry:
            disc = schema.get("discriminator")
            if isinstance(disc, dict):
                schema["discriminator"] = dict(disc)
                schema["discriminator"]["defaultValue"] = overlay_entry["default_discriminator"]

        return schema

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
