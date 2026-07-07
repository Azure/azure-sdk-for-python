#!/usr/bin/env python3
"""Extract document layout into ``<file>.layout.{json,md}`` files.

This is **Stage 1** of the analyzer-authoring loop: before drafting a custom
field schema, you usually want the OCR-and-structure output for a few
representative documents so you can see what labels and headings the model
will be working from.

The script calls the typed ``ContentUnderstandingClient`` using
``begin_analyze_binary`` with the ``prebuilt-documentSearch`` analyzer — the
same call pattern as ``samples/sample_analyze_binary.py``.

For each input file, two artefacts are written next to each other:

* ``<stem>.layout.json`` — the raw service response (``AnalysisResult`` dump).
* ``<stem>.layout.md`` — the markdown rendering returned by the service
  (``result.contents[0].markdown``), ready to read in VS Code.

Usage
-----

    extract_layout.py --input <file-or-folder> --output <dir>

Authentication
--------------

The script honours the standard SDK env-var precedence:

* ``CONTENTUNDERSTANDING_ENDPOINT`` — required.
* ``CONTENTUNDERSTANDING_KEY`` — if present, used via ``AzureKeyCredential``.
* Otherwise, ``DefaultAzureCredential`` is used (e.g. ``az login``).

Password-protected PDFs fall through to the service, which returns a clear
error. The skill deliberately does not depend on third-party PDF libraries.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisResult
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

try:  # pragma: no cover - tiny optional shim
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is optional
    pass


_SUPPORTED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".heif"}


def _iter_inputs(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    for p in sorted(input_path.iterdir()):
        if p.is_file() and p.suffix.lower() in _SUPPORTED_SUFFIXES:
            yield p


def _build_client() -> ContentUnderstandingClient:
    endpoint = os.environ.get("CONTENTUNDERSTANDING_ENDPOINT")
    if not endpoint:
        raise SystemExit(
            "CONTENTUNDERSTANDING_ENDPOINT is not set. "
            "Configure your .env file (see cu-sdk-setup)."
        )
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()
    return ContentUnderstandingClient(endpoint=endpoint, credential=credential)


def _extract_markdown(result: AnalysisResult) -> str:
    """Pull the markdown rendering out of an AnalysisResult, defensively."""

    contents = getattr(result, "contents", None) or []
    for entry in contents:
        markdown = getattr(entry, "markdown", None)
        if markdown:
            return markdown
    return ""


def _result_to_json(result: AnalysisResult) -> dict:
    """Serialize an AnalysisResult to a plain dict for ``json.dump``."""

    # Typed SDK models expose ``as_dict()``; fall back to ``__dict__``.
    if hasattr(result, "as_dict"):
        return result.as_dict()
    return json.loads(json.dumps(result, default=lambda o: getattr(o, "__dict__", str(o))))


def extract_layout(
    inputs: List[Path],
    output_dir: Path,
    *,
    client: ContentUnderstandingClient,
    analyzer_id: str = "prebuilt-documentSearch",
) -> Tuple[int, int]:
    """Run layout extraction. Returns ``(ok_count, fail_count)``."""

    output_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = 0

    for file_path in inputs:
        stem = file_path.stem
        try:
            print(f"[RUN ] {file_path} → {output_dir}/{stem}.layout.{{json,md}}")
            with file_path.open("rb") as fh:
                poller = client.begin_analyze_binary(
                    analyzer_id=analyzer_id,
                    binary_input=fh.read(),
                )
            result: AnalysisResult = poller.result()
        except Exception as exc:  # noqa: BLE001 - surface to operator
            print(f"[FAIL] {file_path}: {exc}", file=sys.stderr)
            fail += 1
            continue

        (output_dir / f"{stem}.layout.json").write_text(
            json.dumps(_result_to_json(result), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (output_dir / f"{stem}.layout.md").write_text(
            _extract_markdown(result), encoding="utf-8"
        )
        ok += 1

    return ok, fail


def _parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract document layout (.layout.json + .layout.md) for each "
            "input file. Stage 1 of the cu-sdk-author-analyzer workflow."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to an input file or a folder of input files.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Directory to write .layout.json + .layout.md into.",
    )
    parser.add_argument(
        "--analyzer-id",
        default="prebuilt-documentSearch",
        help="Layout analyzer to use (default: prebuilt-documentSearch).",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv)

    input_path = args.input
    if not input_path.exists():
        print(f"input does not exist: {input_path}", file=sys.stderr)
        return 2

    inputs = list(_iter_inputs(input_path))
    if not inputs:
        print(
            f"no supported documents found under {input_path} "
            f"(supported: {sorted(_SUPPORTED_SUFFIXES)})",
            file=sys.stderr,
        )
        return 2

    client = _build_client()
    ok, fail = extract_layout(inputs, args.output, client=client, analyzer_id=args.analyzer_id)
    print(f"\n[DONE] {ok} ok, {fail} failed; output → {args.output}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
