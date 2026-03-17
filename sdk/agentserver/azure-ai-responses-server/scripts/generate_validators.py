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

    discovered_roots = discover_post_request_roots(spec)
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
