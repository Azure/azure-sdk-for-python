#!/usr/bin/env python3
"""Classify-and-route: create N inner analyzers + 1 outer classifier, batch-test.

This is the multi-doc-type analogue of ``../cu-sdk-author-analyzer/scripts/
create_and_test.py``. Use it when a single input file (or folder) contains
mixed document types — for example, an invoice + bank statement + loan
application in one PDF.

Flow
----

1. Validate every inner schema and the outer classifier schema locally
   (catches typos in ``baseAnalyzerId``, missing ``contentCategories``,
   etc.).
2. Verify every category in the outer schema that declares an ``analyzerId``
   placeholder has a matching ``--inner-schema`` entry.
3. Create each inner analyzer.
4. Patch the outer schema's ``contentCategories[*].analyzerId`` with the
   real inner analyzer IDs.
5. Create the outer (classifier) analyzer.
6. Batch-analyze each input file; dump per-doc result JSON.
7. Print a **category-aware** stdout summary: per-category fill rate
   denominator is the number of segments classified into that category — not
   the total number of segments across the packet.

Authentication
--------------

Same precedence as the sibling script and ``samples/sample_create_classifier.py``:
``CONTENTUNDERSTANDING_KEY`` → ``AzureKeyCredential``; otherwise
``DefaultAzureCredential`` (e.g. ``az login``).

Usage
-----

::

    create_and_test_router.py \\
        --outer-schema .local_only/schemas/classifier.json \\
        --inner-schema invoice=.local_only/schemas/invoice.json \\
        --inner-schema bank_statement=.local_only/schemas/bank_statement.json \\
        --inner-schema loan_application=.local_only/schemas/loan_application.json \\
        --input samples/sample_files/mixed_financial_docs.pdf \\
        --output .local_only/test_results/v1
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:  # pragma: no cover
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


# Reuse helpers from the sibling script via direct file load.
_HERE = Path(__file__).resolve().parent
_SHARED_DIR = _HERE.parent.parent / "_shared"
_SIBLING_CREATE_AND_TEST = (
    _HERE.parent.parent
    / "cu-sdk-author-analyzer"
    / "scripts"
    / "create_and_test.py"
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_validator = _load_module(
    "_skill_schema_validator", _SHARED_DIR / "schema_validator.py"
)
_create_and_test = _load_module(
    "_skill_create_and_test", _SIBLING_CREATE_AND_TEST
)

_iter_inputs = _create_and_test._iter_inputs
_result_to_dict = _create_and_test._result_to_dict
_field_value = _create_and_test._field_value
_build_client = _create_and_test._build_client
_schema_hash = _create_and_test.schema_hash
_ensure_analyzer = _create_and_test.ensure_analyzer
_strip_comments = _create_and_test._strip_comments


# ---------------------------------------------------------------------------
# Inner / outer schema wiring
# ---------------------------------------------------------------------------


def _parse_inner_arg(values: List[str]) -> Dict[str, Path]:
    """Parse ``--inner-schema alias=path`` repeats into ``{alias: Path}``."""

    result: Dict[str, Path] = {}
    for entry in values:
        if "=" not in entry:
            raise SystemExit(
                f"--inner-schema must be alias=path, got: {entry!r}"
            )
        alias, _, raw_path = entry.partition("=")
        alias = alias.strip()
        path = Path(raw_path.strip())
        if not alias:
            raise SystemExit(f"--inner-schema alias empty in: {entry!r}")
        if alias in result:
            raise SystemExit(f"--inner-schema alias repeated: {alias!r}")
        result[alias] = path
    return result


def _discover_inner_from_dir(
    outer_schema: Dict[str, Any], schema_dir: Path
) -> Dict[str, Path]:
    """Auto-build {alias: path} from a directory.

    For every category in the outer schema whose ``analyzerId`` is a non-
    prebuilt alias, find a matching JSON file in ``schema_dir``. The
    matching rule is: filename stem == alias, or stem startswith
    ``<alias>_`` (picks the alphabetically last match, so ``invoice_v2.json``
    wins over ``invoice_v1.json``).
    """

    if not schema_dir.is_dir():
        raise SystemExit(f"--schema-dir is not a directory: {schema_dir}")

    categories = (outer_schema.get("config") or {}).get("contentCategories") or {}
    aliases: List[str] = []
    for entry in categories.values():
        if not isinstance(entry, dict):
            continue
        alias = entry.get("analyzerId")
        if not isinstance(alias, str) or alias.startswith("prebuilt-"):
            continue
        aliases.append(alias)

    json_files = sorted(schema_dir.glob("*.json"))
    resolved: Dict[str, Path] = {}
    missing: List[str] = []
    for alias in aliases:
        matches = [
            p for p in json_files
            if p.stem == alias or p.stem.startswith(f"{alias}_")
        ]
        if not matches:
            missing.append(alias)
            continue
        resolved[alias] = matches[-1]  # alphabetically last → newest version

    if missing:
        raise SystemExit(
            "--schema-dir could not resolve inner schemas for: "
            f"{missing}. Looked in {schema_dir} for files named "
            "<alias>.json or <alias>_*.json."
        )
    return resolved


def _validate_all(
    outer_schema_path: Path, inner_paths: Mapping[str, Path]
) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """Validate outer + inner schemas, return loaded JSON for each.

    Exits with code 2 if anything fails.
    """

    failures: List[str] = []

    ok, errors = _validator.validate_schema_file(outer_schema_path)
    if not ok:
        failures.extend(f"[outer] {e}" for e in errors)

    inner_schemas: Dict[str, Dict[str, Any]] = {}
    for alias, p in inner_paths.items():
        if not p.exists():
            failures.append(f"[inner:{alias}] schema file not found: {p}")
            continue
        ok, errors = _validator.validate_schema_file(p)
        if not ok:
            failures.extend(f"[inner:{alias}] {e}" for e in errors)
            continue
        inner_schemas[alias] = _strip_comments(json.loads(p.read_text(encoding="utf-8")))

    if failures:
        for line in failures:
            print(f"[VALIDATE] {line}", file=sys.stderr)
        raise SystemExit(2)

    outer_schema = _strip_comments(json.loads(outer_schema_path.read_text(encoding="utf-8")))

    # Pre-flight: every inner schema with fieldSchema needs models.completion
    # unless resource defaults are set. Surface this up front — otherwise the
    # service polls to InvalidRequest only AFTER begin_create_analyzer
    # returns success.
    for alias, schema in inner_schemas.items():
        if isinstance(schema, dict) and "fieldSchema" in schema:
            models = schema.get("models") or {}
            if not (isinstance(models, dict) and models.get("completion")):
                print(
                    f"[WARN]    inner schema {alias!r} has fieldSchema but no "
                    "models.completion; this will fail unless resource defaults "
                    "are configured (see samples/sample_update_defaults.py).",
                    file=sys.stderr,
                )

    return outer_schema, inner_schemas


def _wire_inner_ids(
    outer_schema: Dict[str, Any], alias_to_real_id: Mapping[str, str]
) -> Tuple[Dict[str, Any], List[str]]:
    """Patch outer ``contentCategories[*].analyzerId`` placeholders.

    Returns ``(patched_outer_schema, errors)``. An empty ``errors`` list
    means every referenced alias resolved.
    """

    errors: List[str] = []
    patched = json.loads(json.dumps(outer_schema))  # deep copy
    categories = (patched.get("config") or {}).get("contentCategories") or {}

    for cat_name, entry in categories.items():
        if not isinstance(entry, dict):
            continue
        alias = entry.get("analyzerId")
        if alias is None:
            continue
        # Service prebuilts ("prebuilt-invoice", "prebuilt-receipt", ...)
        # are valid analyzer IDs as-is and don't need a --inner-schema.
        if isinstance(alias, str) and alias.startswith("prebuilt-"):
            continue
        real = alias_to_real_id.get(alias)
        if real is None:
            errors.append(
                f"category {cat_name!r} references analyzerId={alias!r}, but "
                f"no --inner-schema entry matches alias {alias!r}. "
                f"Known aliases: {sorted(alias_to_real_id)}"
            )
            continue
        entry["analyzerId"] = real

    # Catch unused inner schemas (cheap typo check).
    used = {
        e.get("analyzerId")
        for e in categories.values()
        if isinstance(e, dict)
    }
    for alias in alias_to_real_id:
        if alias_to_real_id[alias] not in used:
            errors.append(
                f"--inner-schema {alias!r} was supplied but no category in "
                f"the outer schema routes to it"
            )

    return patched, errors


# ---------------------------------------------------------------------------
# Category-aware summary
# ---------------------------------------------------------------------------


def summarize_routed(
    results: List[Tuple[str, Dict[str, Any]]],
) -> str:
    """Build a category-aware stdout summary.

    Denominator per category = segments whose ``category`` matches, not the
    total number of segments across the packet — so a field that's only
    meaningful in one category doesn't get penalised by other categories'
    segment counts.
    """

    # category → field → list[(doc_name, value, confidence)]
    table: Dict[str, Dict[str, List[Tuple[str, Any, Optional[float]]]]] = {}
    # category → total segment count
    seg_counts: Dict[str, int] = {}

    for doc_name, doc in results:
        for content in doc.get("contents") or []:
            category = content.get("category") or "(uncategorized)"
            seg_counts[category] = seg_counts.get(category, 0) + 1
            fields = content.get("fields") or {}
            for fname, field_val in fields.items():
                if not isinstance(field_val, dict):
                    continue
                row = table.setdefault(category, {}).setdefault(fname, [])
                row.append((doc_name, _field_value(field_val), field_val.get("confidence")))

    if not table and not seg_counts:
        return "[SUMMARY] no segments classified."

    lines: List[str] = ["", "=" * 72, "[SUMMARY] (category-aware)"]
    for category in sorted(seg_counts):
        denom = seg_counts[category]
        per_field = table.get(category, {})
        header = f"category: {category}  ({denom} segments)"
        lines.append("")
        lines.append(header)
        lines.append("-" * len(header))
        if not per_field:
            lines.append("  (no extracted fields — classification-only or missing analyzerId)")
            continue
        lines.append(f"  {'field':<30} fill rate   avg conf")
        for fname in sorted(per_field):
            rows = per_field[fname]
            filled = [r for r in rows if r[1] not in (None, "", [], {})]
            fill_rate = (len(filled) / denom) if denom else 0.0
            # Only consider confidence from rows where the value was actually
            # extracted; reporting confidence for empty fields is misleading.
            confidences = [
                r[2]
                for r in rows
                if r[1] not in (None, "", [], {})
                and isinstance(r[2], (int, float))
            ]
            avg_conf = (sum(confidences) / len(confidences)) if confidences else None
            conf_str = f"{avg_conf:.3f}" if avg_conf is not None else "  n/a"
            lines.append(f"  {fname:<30} {fill_rate * 100:>5.1f}%      {conf_str}")

    lowest: List[Tuple[float, str, str, str]] = []
    for category, per_field in table.items():
        for fname, rows in per_field.items():
            for doc_name, value, conf in rows:
                if value in (None, "", [], {}):
                    continue
                if isinstance(conf, (int, float)):
                    lowest.append((float(conf), category, fname, doc_name))
    lowest.sort(key=lambda x: x[0])
    if lowest:
        lines.append("")
        lines.append("lowest-confidence fields across all categories:")
        for conf, category, fname, doc_name in lowest[:3]:
            lines.append(f"  {conf:.3f}  [{category}] {fname}  ({doc_name})")
    lines.append("=" * 72)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Service flow
# ---------------------------------------------------------------------------


def create_inner_analyzers(
    client,
    inner_schemas: Mapping[str, Dict[str, Any]],
    *,
    id_prefix: str,
    reuse: bool = False,
) -> Tuple[Dict[str, str], Dict[str, bool]]:
    """Create each inner analyzer; return ``({alias: real_id}, {alias: reused})``."""

    alias_to_id: Dict[str, str] = {}
    reused_map: Dict[str, bool] = {}
    for alias, schema in inner_schemas.items():
        if reuse:
            real_id = f"{id_prefix}_inner_{alias}_{_schema_hash(schema)}"
            reused_map[alias] = _ensure_analyzer(client, real_id, schema)
        else:
            real_id = f"{id_prefix}_inner_{alias}"
            print(f"[CREATE-INNER] {alias} → {real_id}")
            poller = client.begin_create_analyzer(analyzer_id=real_id, resource=schema)
            poller.result()
            reused_map[alias] = False
        alias_to_id[alias] = real_id
    return alias_to_id, reused_map


def run(
    *,
    outer_schema_path: Path,
    inner_schema_paths: Mapping[str, Path],
    input_path: Path,
    output_dir: Path,
    analyzer_id: Optional[str],
    ephemeral: bool,
    reuse: bool,
) -> int:
    outer_schema, inner_schemas = _validate_all(outer_schema_path, inner_schema_paths)

    inputs = list(_iter_inputs(input_path))
    if not inputs:
        print(f"no supported documents found under {input_path}", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    if not analyzer_id:
        if reuse:
            # Outer hash depends on patched analyzerIds, which depend on
            # inner hashes — fold them in so any inner schema edit also
            # gives the outer a new ID.
            inner_hash_blob = "".join(
                f"{a}:{_schema_hash(s)};" for a, s in sorted(inner_schemas.items())
            )
            outer_id_input = {"outer": outer_schema, "inner": inner_hash_blob}
            analyzer_id = f"{outer_schema_path.stem}_{_schema_hash(outer_id_input)}"
        else:
            analyzer_id = f"{outer_schema_path.stem}_{int(time.time())}"

    client = _build_client()

    alias_to_id: Dict[str, str] = {}
    outer_reused = False
    fail = 0
    results: List[Tuple[str, Dict[str, Any]]] = []
    try:
        alias_to_id, _inner_reused = create_inner_analyzers(
            client, inner_schemas, id_prefix=analyzer_id, reuse=reuse
        )

        patched_outer, wire_errors = _wire_inner_ids(outer_schema, alias_to_id)
        if wire_errors:
            for e in wire_errors:
                print(f"[VALIDATE] {e}", file=sys.stderr)
            return 2

        if reuse:
            outer_reused = _ensure_analyzer(client, analyzer_id, patched_outer)
        else:
            print(f"[CREATE-OUTER] {analyzer_id}")
            poller = client.begin_create_analyzer(analyzer_id=analyzer_id, resource=patched_outer)
            poller.result()
            print(f"[CREATE-OUTER] {analyzer_id} ready")

        for file_path in inputs:
            out_path = output_dir / f"{file_path.stem}.json"
            try:
                print(f"[ANALYZE] {file_path} → {out_path}")
                with file_path.open("rb") as fh:
                    p = client.begin_analyze_binary(
                        analyzer_id=analyzer_id, binary_input=fh.read()
                    )
                result = p.result()
            except Exception as exc:  # noqa: BLE001
                print(f"[FAIL]    {file_path}: {exc}", file=sys.stderr)
                fail += 1
                continue
            doc = _result_to_dict(result)
            out_path.write_text(
                json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            # Best-effort LLM-ready markdown next to the JSON. For
            # classify-and-route results, to_llm_input expands each segment
            # into its own block with the category in the YAML front matter.
            try:
                from azure.ai.contentunderstanding import to_llm_input  # type: ignore

                llm_text = to_llm_input(result)
                out_path.with_suffix(".llm.md").write_text(llm_text, encoding="utf-8")
            except Exception:  # noqa: BLE001 — best-effort
                pass
            results.append((out_path.stem, doc))
    finally:
        if ephemeral:
            for analyzer_id_to_delete in [analyzer_id, *alias_to_id.values()]:
                try:
                    print(f"[CLEANUP] delete {analyzer_id_to_delete}")
                    client.delete_analyzer(analyzer_id=analyzer_id_to_delete)
                except Exception as exc:  # noqa: BLE001
                    print(
                        f"[CLEANUP] failed for {analyzer_id_to_delete}: {exc}",
                        file=sys.stderr,
                    )
        else:
            kept = [analyzer_id, *alias_to_id.values()]
            print(
                f"[KEEP]    analyzers retained ({len(kept)}): {kept} "
                "(use --ephemeral to delete)"
            )

    print(summarize_routed(results))
    return 0 if fail == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate, create, and batch-test a classify-and-route pipeline "
            "(outer classifier + N inner extractors)."
        )
    )
    parser.add_argument(
        "--outer-schema", required=True, type=Path, help="Outer (classifier) schema JSON."
    )
    parser.add_argument(
        "--inner-schema",
        action="append",
        default=[],
        metavar="ALIAS=PATH",
        help=(
            "Inner extractor schema, given as alias=path. The alias must "
            "match the analyzerId placeholder used in the outer schema's "
            "contentCategories. Repeat for each inner extractor. "
            "Mutually exclusive with --schema-dir."
        ),
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=None,
        help=(
            "Directory containing inner schema files. Auto-maps each "
            "non-prebuilt analyzerId alias in the outer schema to "
            "<alias>.json or <alias>_*.json in this directory (newest "
            "version wins). Mutually exclusive with --inner-schema."
        ),
    )
    parser.add_argument(
        "--input", required=True, type=Path, help="Input file or folder."
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Directory to write per-document result JSON into.",
    )
    parser.add_argument(
        "--analyzer-id",
        default=None,
        help="Outer analyzer ID (default: <outer-schema-stem>_<unix-timestamp>). "
        "Inner analyzers are named <analyzer-id>_inner_<alias>.",
    )
    parser.add_argument(
        "--ephemeral",
        action="store_true",
        help="Delete inner + outer analyzers at the end of the run.",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help=(
            "Name analyzers using a sha1 of the schema instead of a "
            "timestamp, and skip creation when an analyzer with that ID "
            "already exists. Use this to avoid piling up stale analyzers "
            "while iterating."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    if not args.outer_schema.exists():
        print(f"outer schema not found: {args.outer_schema}", file=sys.stderr)
        return 2
    if not args.input.exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 2

    if args.inner_schema and args.schema_dir:
        print(
            "--inner-schema and --schema-dir are mutually exclusive",
            file=sys.stderr,
        )
        return 2
    if not args.inner_schema and not args.schema_dir:
        print(
            "provide --schema-dir DIR or one or more --inner-schema alias=path",
            file=sys.stderr,
        )
        return 2

    if args.schema_dir:
        outer_schema_preview = json.loads(
            args.outer_schema.read_text(encoding="utf-8")
        )
        inner_paths = _discover_inner_from_dir(
            outer_schema_preview, args.schema_dir
        )
        print(
            "[SCHEMA-DIR] resolved: "
            + ", ".join(f"{a}={p.name}" for a, p in inner_paths.items())
        )
    else:
        inner_paths = _parse_inner_arg(args.inner_schema)

    return run(
        outer_schema_path=args.outer_schema,
        inner_schema_paths=inner_paths,
        input_path=args.input,
        output_dir=args.output,
        analyzer_id=args.analyzer_id,
        ephemeral=args.ephemeral,
        reuse=args.reuse,
    )


if __name__ == "__main__":
    sys.exit(main())
