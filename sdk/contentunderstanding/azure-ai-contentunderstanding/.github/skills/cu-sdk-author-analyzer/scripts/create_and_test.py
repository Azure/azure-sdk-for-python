#!/usr/bin/env python3
"""Create a custom analyzer from a JSON schema and batch-test it.

This is **Stage 2** of the analyzer-authoring loop:

1. Validate the schema locally (catches typos in ``baseAnalyzerId``, missing
   ``fieldSchema``, malformed ``contentCategories`` routes — see
   ``_shared/schema_validator.py``).
2. Create the analyzer via ``begin_create_analyzer`` and wait for it to be
   ready.
3. For each input document, call ``begin_analyze_binary`` and dump the
   per-document result JSON under ``--output``.
4. Print a stdout summary: per-field fill rate and the three lowest-confidence
   ``(field, document)`` pairs. No CSV — read the per-doc JSON for full
   detail.
5. By default the analyzer is **kept** in the resource so you can re-use it.
   Pass ``--ephemeral`` to delete it at the end of the run.

Exit codes
----------

* ``0`` — every document analyzed successfully.
* ``1`` — at least one service-side failure.
* ``2`` — user error (schema validator failure, missing flags, bad input
  paths). The script exits before any service call in this case.

Authentication
--------------

Same precedence as ``samples/sample_create_analyzer.py``:
``CONTENTUNDERSTANDING_KEY`` → ``AzureKeyCredential``; otherwise
``DefaultAzureCredential`` (e.g. ``az login``).

Usage
-----

    create_and_test.py \\
        --schema .local_only/schemas/invoice_v1.json \\
        --input samples/sample_files/mixed_financial_docs.pdf \\
        --output .local_only/test_results/v1
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:  # pragma: no cover
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


# ---------------------------------------------------------------------------
# _shared/schema_validator loader (no package; load via importlib)
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
_SHARED_DIR = _HERE.parent.parent / "_shared"


def _load_shared_validator():
    spec = importlib.util.spec_from_file_location(
        "_skill_schema_validator", _SHARED_DIR / "schema_validator.py"
    )
    if not spec or not spec.loader:  # pragma: no cover - defensive
        raise SystemExit(
            "could not locate _shared/schema_validator.py (expected at "
            f"{_SHARED_DIR / 'schema_validator.py'})"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SUPPORTED_SUFFIXES = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif",
    ".bmp",
    ".heif",
    ".mp4",
    ".mov",
    ".wav",
    ".mp3",
    ".m4a",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _iter_inputs(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    for p in sorted(input_path.iterdir()):
        if p.is_file() and p.suffix.lower() in _SUPPORTED_SUFFIXES:
            yield p


def _result_to_dict(result: Any) -> Dict[str, Any]:
    if hasattr(result, "as_dict"):
        return result.as_dict()
    return json.loads(json.dumps(result, default=lambda o: getattr(o, "__dict__", str(o))))


def _strip_comments(obj: Any) -> Any:
    """Recursively drop any dict key whose name starts with ``_``.

    Lets the template carry ``_comment`` / ``_optional_*`` documentation keys
    without poisoning the service request body. Pure, returns a new object.
    """
    if isinstance(obj, dict):
        return {k: _strip_comments(v) for k, v in obj.items() if not (isinstance(k, str) and k.startswith("_"))}
    if isinstance(obj, list):
        return [_strip_comments(v) for v in obj]
    return obj


def _iter_fields(doc: Dict[str, Any]) -> Iterable[Tuple[str, str, Dict[str, Any]]]:
    """Yield ``(category, field_path, field_value_dict)`` for each *leaf* field.

    Handles both single-analyzer results (one entry in ``contents``) and
    classify-and-route results (multiple entries, each with ``category``).

    Nested fields are flattened into dotted paths so they show up in the
    summary instead of collapsing to a single ``n/a`` row:

    * ``valueArray`` of ``valueObject``s → ``parent[].child`` rows (one row
      per array item across all docs).
    * ``valueObject`` (non-array) → ``parent.child`` rows.
    * Scalars are yielded as-is.
    """

    def _recurse(prefix: str, field_val: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
        if "valueArray" in field_val and isinstance(field_val["valueArray"], list):
            for item in field_val["valueArray"]:
                if isinstance(item, dict) and "valueObject" in item and isinstance(item["valueObject"], dict):
                    for child_name, child_val in item["valueObject"].items():
                        if isinstance(child_val, dict):
                            yield from _recurse(f"{prefix}[].{child_name}", child_val)
                else:
                    # array of scalars — emit one row per item under prefix
                    yield prefix, item if isinstance(item, dict) else {"valueString": item, "confidence": None}
            return
        if "valueObject" in field_val and isinstance(field_val["valueObject"], dict):
            for child_name, child_val in field_val["valueObject"].items():
                if isinstance(child_val, dict):
                    yield from _recurse(f"{prefix}.{child_name}", child_val)
            return
        yield prefix, field_val

    contents = doc.get("contents") or []
    for content in contents:
        category = content.get("category") or ""
        fields = content.get("fields") or {}
        for fname, field_val in fields.items():
            if isinstance(field_val, dict):
                for path, leaf in _recurse(fname, field_val):
                    yield category, path, leaf


def _field_value(field: Dict[str, Any]) -> Any:
    """Return the scalar value of a field result entry, or None if empty."""

    for key in ("valueString", "valueNumber", "valueInteger", "valueBoolean", "valueDate", "valueTime"):
        if key in field and field[key] not in (None, ""):
            return field[key]
    if "valueArray" in field:
        arr = field["valueArray"]
        return arr if arr else None
    if "valueObject" in field:
        return field["valueObject"] or None
    return None


def summarize(results: List[Tuple[str, Dict[str, Any]]]) -> str:
    """Build the stdout summary string."""

    # category → field → list[(doc_name, value, confidence)]
    table: Dict[str, Dict[str, List[Tuple[str, Any, Optional[float]]]]] = {}
    for doc_name, doc in results:
        for category, fname, field_val in _iter_fields(doc):
            row = table.setdefault(category, {}).setdefault(fname, [])
            row.append((doc_name, _field_value(field_val), field_val.get("confidence")))

    if not table:
        return "[SUMMARY] no fields extracted across any document."

    lines: List[str] = ["", "=" * 72, "[SUMMARY]"]
    for category in sorted(table.keys()):
        per_field = table[category]
        n_docs = len({doc_name for rows in per_field.values() for doc_name, *_ in rows})
        header = f"category: {category or '(single)'}  ({n_docs} document{'s' if n_docs != 1 else ''})"
        lines.append("")
        lines.append(header)
        lines.append("-" * len(header))
        lines.append(f"  {'field':<40} fill rate   avg conf")
        for fname in sorted(per_field):
            rows = per_field[fname]
            denom = len(rows)
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
            lines.append(f"  {fname:<40} {fill_rate * 100:>5.1f}%      {conf_str}")

    # Three lowest-confidence (category, field, doc) triples across the run.
    lowest: List[Tuple[Optional[float], str, str, str]] = []
    for category, per_field in table.items():
        for fname, rows in per_field.items():
            for doc_name, value, conf in rows:
                if value in (None, "", [], {}):
                    continue
                if isinstance(conf, (int, float)):
                    lowest.append((conf, category, fname, doc_name))
    lowest.sort(key=lambda x: (x[0] if x[0] is not None else 1.0))
    if lowest:
        lines.append("")
        lines.append("lowest-confidence fields:")
        for conf, category, fname, doc_name in lowest[:3]:
            cat = f"[{category}]" if category else ""
            lines.append(f"  {conf:.3f}  {cat} {fname}  ({doc_name})")
    lines.append("=" * 72)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Service interaction
# ---------------------------------------------------------------------------


def _build_client():
    from azure.ai.contentunderstanding import ContentUnderstandingClient
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ.get("CONTENTUNDERSTANDING_ENDPOINT")
    if not endpoint:
        raise SystemExit(
            "CONTENTUNDERSTANDING_ENDPOINT is not set. "
            "Configure your .env file (see cu-sdk-setup)."
        )
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()
    return ContentUnderstandingClient(endpoint=endpoint, credential=credential)


def create_analyzer(client, analyzer_id: str, schema: Dict[str, Any]) -> None:
    """Create an analyzer and wait until it is ready.

    Passes the schema dict directly as the request body — the SDK's
    ``begin_create_analyzer`` accepts ``Union[ContentAnalyzer, JSON, IO]``.
    """

    print(f"[CREATE] analyzer_id={analyzer_id}")
    poller = client.begin_create_analyzer(analyzer_id=analyzer_id, resource=schema)
    poller.result()
    print(f"[CREATE] {analyzer_id} ready")


def schema_hash(schema: Dict[str, Any]) -> str:
    """Stable 8-char hash of a schema dict, for --reuse naming."""

    blob = json.dumps(schema, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()[:8]


def ensure_analyzer(client, analyzer_id: str, schema: Dict[str, Any]) -> bool:
    """Create the analyzer if it doesn't already exist. Return True if reused."""

    try:
        client.get_analyzer(analyzer_id=analyzer_id)
        print(f"[REUSE]  analyzer {analyzer_id} already exists")
        return True
    except Exception:  # noqa: BLE001 — ResourceNotFoundError or transport
        pass
    create_analyzer(client, analyzer_id, schema)
    return False


def analyze_file(client, analyzer_id: str, file_path: Path) -> Tuple[Dict[str, Any], Optional[str]]:
    """Run analysis and return (result_dict, llm_markdown_or_None).

    ``llm_markdown`` is produced via the SDK's ``to_llm_input`` helper. It is
    safe to fall through to ``None`` if the helper raises (e.g. on a result
    shape it doesn't recognise) — the raw JSON is always written.
    """
    with file_path.open("rb") as fh:
        poller = client.begin_analyze_binary(
            analyzer_id=analyzer_id, binary_input=fh.read()
        )
    result = poller.result()
    llm_text: Optional[str] = None
    try:
        from azure.ai.contentunderstanding import to_llm_input  # type: ignore

        llm_text = to_llm_input(result)
    except Exception:  # noqa: BLE001 — best-effort
        llm_text = None
    return _result_to_dict(result), llm_text


def run(
    *,
    schema_path: Path,
    input_path: Path,
    output_dir: Path,
    analyzer_id: Optional[str],
    iterations: int,
    ephemeral: bool,
    reuse: bool,
) -> int:
    # Validate
    validator = _load_shared_validator()
    ok, errors = validator.validate_schema_file(schema_path)
    if not ok:
        for e in errors:
            print(f"[VALIDATE] {e}", file=sys.stderr)
        return 2

    with schema_path.open("r", encoding="utf-8") as fp:
        raw_schema = json.load(fp)
    schema = _strip_comments(raw_schema)

    # Pre-flight: warn if the schema has fieldSchema but no completion model.
    # Without resource defaults set (see samples/sample_update_defaults.py)
    # the service polls to InvalidRequest only AFTER begin_create_analyzer
    # returns success — surface the risk up front.
    if isinstance(schema, dict) and "fieldSchema" in schema:
        models = schema.get("models") or {}
        if not (isinstance(models, dict) and models.get("completion")):
            print(
                "[WARN]   schema has fieldSchema but no models.completion; "
                "this will fail unless resource defaults are configured "
                "(see samples/sample_update_defaults.py).",
                file=sys.stderr,
            )

    inputs = list(_iter_inputs(input_path))
    if not inputs:
        print(
            f"no supported documents found under {input_path}", file=sys.stderr
        )
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    if not analyzer_id:
        if reuse:
            analyzer_id = f"{schema_path.stem}_{schema_hash(schema)}"
        else:
            analyzer_id = f"{schema_path.stem}_{int(time.time())}"

    client = _build_client()

    fail = 0
    reused = False
    results: List[Tuple[str, Dict[str, Any]]] = []
    try:
        if reuse:
            reused = ensure_analyzer(client, analyzer_id, schema)
        else:
            create_analyzer(client, analyzer_id, schema)
        for file_path in inputs:
            for iter_idx in range(1, iterations + 1):
                suffix = f"_iter{iter_idx:03d}" if iterations > 1 else ""
                out_path = output_dir / f"{file_path.stem}{suffix}.json"
                try:
                    print(f"[ANALYZE] {file_path} → {out_path}")
                    doc, llm_text = analyze_file(client, analyzer_id, file_path)
                except Exception as exc:  # noqa: BLE001
                    print(f"[FAIL]   {file_path}: {exc}", file=sys.stderr)
                    fail += 1
                    continue

                out_path.write_text(
                    json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                if llm_text is not None:
                    llm_path = out_path.with_suffix(".llm.md")
                    llm_path.write_text(llm_text, encoding="utf-8")
                results.append((out_path.stem, doc))
    finally:
        if ephemeral:
            try:
                print(f"[CLEANUP] delete analyzer {analyzer_id}")
                client.delete_analyzer(analyzer_id=analyzer_id)
            except Exception as exc:  # noqa: BLE001
                print(f"[CLEANUP] delete failed: {exc}", file=sys.stderr)
        elif reused:
            print(f"[KEEP]    reused analyzer {analyzer_id} retained")
        else:
            print(f"[KEEP]    analyzer {analyzer_id} retained (use --ephemeral to delete)")

    print(summarize(results))
    return 0 if fail == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a schema, create the analyzer, batch-test it against "
            "input documents, and print a stdout summary."
        )
    )
    parser.add_argument("--schema", required=True, type=Path, help="Schema JSON file.")
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to an input file or folder of input files.",
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
        help="Analyzer ID (default: <schema-stem>_<unix-timestamp>).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Run each document this many times (default: 1). N>1 emits "
        "<doc>_iterNNN.json suffixes for stability testing.",
    )
    parser.add_argument(
        "--ephemeral",
        action="store_true",
        help="Delete the created analyzer at the end of the run.",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help=(
            "Name the analyzer <schema-stem>_<sha1[:8]> instead of "
            "appending a unix timestamp, and skip creation if an analyzer "
            "with that ID already exists. Use this when iterating on a "
            "schema to avoid piling up stale analyzers."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    if args.iterations < 1:
        print("--iterations must be >= 1", file=sys.stderr)
        return 2
    if not args.schema.exists():
        print(f"schema not found: {args.schema}", file=sys.stderr)
        return 2
    if not args.input.exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 2

    return run(
        schema_path=args.schema,
        input_path=args.input,
        output_dir=args.output,
        analyzer_id=args.analyzer_id,
        iterations=args.iterations,
        ephemeral=args.ephemeral,
        reuse=args.reuse,
    )


if __name__ == "__main__":
    sys.exit(main())
