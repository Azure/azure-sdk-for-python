#!/usr/bin/env python3
"""Generate Python payload validators from an OpenAPI document."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.validator_emitter import build_validator_module
    from scripts.validator_schema_walker import SchemaWalker, discover_post_request_roots
except ModuleNotFoundError:
    from validator_emitter import build_validator_module
    from validator_schema_walker import SchemaWalker, discover_post_request_roots


def _load_spec(input_path: Path) -> dict[str, Any]:
    """Load a JSON or YAML OpenAPI document from disk."""
    text = input_path.read_text(encoding="utf-8")
    try:
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return loaded
    except json.JSONDecodeError:
        pass

    try:
        import yaml  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise ValueError(
            f"unable to parse OpenAPI file '{input_path}'. Expected JSON, or install PyYAML for YAML input."
        ) from exc

    loaded_yaml = yaml.safe_load(text)
    if not isinstance(loaded_yaml, dict):
        raise ValueError(f"OpenAPI file '{input_path}' must contain a top-level object")
    return loaded_yaml


def _build_output(spec: dict[str, Any], roots: list[str]) -> str:
    """Create deterministic validator module source text."""
    schemas = spec.get("components", {}).get("schemas", {})
    if not isinstance(schemas, dict):
        schemas = {}
    else:
        schemas = dict(schemas)

    def _find_create_response_inline_schema() -> dict[str, Any] | None:
        paths = spec.get("paths", {})
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            if "responses" not in str(path).lower():
                continue
            post = methods.get("post")
            if not isinstance(post, dict):
                continue
            request_body = post.get("requestBody", {})
            content = request_body.get("content", {}).get("application/json", {})
            schema = content.get("schema", {})
            if isinstance(schema, dict) and "anyOf" in schema:
                branches = schema.get("anyOf", [])
                if isinstance(branches, list) and branches and isinstance(branches[0], dict):
                    return branches[0]
            if isinstance(schema, dict) and "oneOf" in schema:
                branches = schema.get("oneOf", [])
                if isinstance(branches, list) and branches and isinstance(branches[0], dict):
                    return branches[0]
            if isinstance(schema, dict):
                return schema
        return None

    for root in roots:
        if root in schemas:
            continue
        if root == "CreateResponse":
            inline_schema = _find_create_response_inline_schema()
            if isinstance(inline_schema, dict):
                schemas[root] = inline_schema

    # If explicit roots are provided, respect them and skip route-wide discovery.
    discovered_roots = [] if roots else discover_post_request_roots(spec)
    merged_roots: list[str] = []
    seen: set[str] = set()
    for root in [*roots, *discovered_roots]:
        if root and root not in seen:
            seen.add(root)
            merged_roots.append(root)

    walker = SchemaWalker(schemas)
    for root in merged_roots:
        walker.walk(root)

    reachable = walker.reachable if walker.reachable else schemas
    effective_roots = merged_roots if merged_roots else sorted(reachable)
    return build_validator_module(reachable, effective_roots)


def main() -> int:
    """Run the validator generator CLI."""
    parser = argparse.ArgumentParser(description="Generate Python payload validators from OpenAPI")
    parser.add_argument("--input", required=True, help="Path to OpenAPI JSON file")
    parser.add_argument("--output", required=True, help="Output Python module path")
    parser.add_argument("--root-schemas", default="", help="Comma-separated root schema names")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    roots = [part.strip() for part in args.root_schemas.split(",") if part.strip()]

    spec = _load_spec(input_path)
    output = _build_output(spec, roots)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
