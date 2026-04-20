# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""LLM input helper for Azure AI Content Understanding.

Provides ``to_llm_input`` — a single public function that converts
``AnalysisResult`` objects into LLM-friendly text (YAML front matter
+ markdown).
"""

from __future__ import annotations

import datetime
import math
import re
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import (
        AnalysisContent,
        AnalysisResult,
        ContentField,
        DocumentContent,
        DocumentPage,
    )
    from azure.core.exceptions import ODataV4Format


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def to_llm_input(
    result: "AnalysisResult",
    *,
    include_fields: bool = True,
    include_markdown: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Convert a CU analysis result into LLM-friendly text.

    Produces a formatted text string from the analysis result,
    suitable for injecting into an LLM prompt, storing in a vector
    database, or passing as tool output.

    For single-content results (documents, images), the output is a
    flat text block. For multi-segment results (video, audio), each
    segment is rendered with its time range. For document
    classification results (parent + categorized children), the
    helper automatically skips the parent and renders each child with
    its category label.

    :param result: The ``AnalysisResult`` from a CU analyze operation.
    :type result: ~azure.ai.contentunderstanding.models.AnalysisResult
    :keyword include_fields: Whether to include structured fields in the
        output. Defaults to True. Set to False for markdown-only
        output (smaller token footprint, no structured data).
    :paramtype include_fields: bool
    :keyword include_markdown: Whether to include markdown content in the
        output. Defaults to True. Set to False for fields-only
        output.
    :paramtype include_markdown: bool
    :keyword metadata: Optional dict of user-supplied key-value pairs to
        include in the YAML front matter. Common keys include
        ``"source"`` (filename), ``"department"``,
        ``"batch_id"``, etc. Metadata keys are placed after
        ``contentType`` and before auto-detected keys
        (``timeRange``, ``category``, ``pages``).
    :paramtype metadata: dict[str, Any] or None
    :returns: A formatted text string with YAML front matter followed
        by markdown content.
    :rtype: str
    :raises TypeError: If *result* is not an ``AnalysisResult``.

    Example::

        from azure.ai.contentunderstanding import (
            ContentUnderstandingClient,
            to_llm_input,
        )
        from azure.identity import DefaultAzureCredential

        client = ContentUnderstandingClient(endpoint, DefaultAzureCredential())
        poller = client.begin_analyze(
            analyzer_id="prebuilt-invoice",
            inputs=[{"source": {"kind": "url", "url": url}}],
        )
        result = poller.result()
        text = to_llm_input(result)
    """
    from .models import AnalysisResult as _AnalysisResult

    if not isinstance(result, _AnalysisResult):
        raise TypeError(f"Expected AnalysisResult, got {type(result).__name__}")

    if not result.contents:
        return ""

    contents = _get_renderable_contents(result.contents)
    if not contents:
        return ""

    from .models import AudioVisualContent as _AV

    av_count = sum(1 for c in contents if isinstance(c, _AV))

    blocks: List[str] = []
    for content in contents:
        block = _render_content_block(
            content,
            result,
            include_fields=include_fields,
            include_markdown=include_markdown,
            metadata=metadata,
            is_multi_segment=(av_count > 1),
        )
        if block:
            blocks.append(block)

    return "\n\n*****\n\n".join(blocks)


# ---------------------------------------------------------------------------
# Field resolution (internal)
# ---------------------------------------------------------------------------


def _resolve_fields(fields: Dict[str, "ContentField"]) -> Dict[str, Any]:
    """Flatten CU ContentField objects into plain Python dicts.

    Recursively resolves ObjectField and ArrayField values using each
    field's ``.value`` convenience property.

    :param fields: The ``fields`` dict from an ``AnalysisContent`` object.
    :type fields: dict[str, ~azure.ai.contentunderstanding.models.ContentField]
    :returns: A plain dict mapping field names to their resolved values.
    :rtype: dict[str, Any]
    """
    resolved: Dict[str, Any] = {}
    for name, field in fields.items():
        val = _resolve_field_value(field)
        if val is not None:
            resolved[name] = val
    return resolved


def _resolve_field_value(
    field: "ContentField",
) -> Any:
    """Resolve a single ContentField to a plain Python value.

    :param field: The content field to resolve.
    :type field: ~azure.ai.contentunderstanding.models.ContentField
    :returns: The resolved plain Python value.
    :rtype: Any
    """
    from .models import ArrayField, ObjectField

    if isinstance(field, ObjectField):
        obj = field.value_object
        return _resolve_fields(obj) if obj else None

    if isinstance(field, ArrayField):
        arr = field.value_array
        if arr:
            items = []
            for item in arr:
                val = _resolve_field_value(item)
                if val is not None:
                    items.append(val)
            return items
        return None

    # Leaf field — use the .value convenience property
    val = field.value  # type: ignore[attr-defined]
    if val is None:
        return None

    # Convert date/time to ISO strings for YAML serialization
    if isinstance(val, (datetime.date, datetime.time)):
        return val.isoformat()

    return val


# ---------------------------------------------------------------------------
# Content rendering
# ---------------------------------------------------------------------------


def _get_renderable_contents(
    contents: "List[AnalysisContent]",
) -> "List[AnalysisContent]":
    """Filter contents for rendering, handling classification hierarchies.

    A "parent" content has ``segments`` but no ``category``. When
    detected, the parent is skipped to avoid text duplication — only
    children (with ``category`` set) are rendered.

    :param contents: The list of analysis contents to filter.
    :type contents: list[~azure.ai.contentunderstanding.models.AnalysisContent]
    :returns: The filtered list of renderable contents.
    :rtype: list[~azure.ai.contentunderstanding.models.AnalysisContent]
    """
    from .models import DocumentContent

    has_parent = False
    for c in contents:
        if isinstance(c, DocumentContent) and c.segments and not c.category:
            has_parent = True
            break

    if not has_parent:
        return list(contents)

    # Return only items that are NOT the parent
    return [
        c
        for c in contents
        if not (isinstance(c, DocumentContent) and c.segments and not c.category)
    ]


def _render_content_block(
    content: "AnalysisContent",
    result: "AnalysisResult",
    *,
    include_fields: bool,
    include_markdown: bool,
    metadata: Optional[Dict[str, Any]],
    is_multi_segment: bool = False,
) -> str:
    """Render a single content item as front matter + body.

    :param content: The content item to render.
    :type content: ~azure.ai.contentunderstanding.models.AnalysisContent
    :param result: The full analysis result (used for warnings).
    :type result: ~azure.ai.contentunderstanding.models.AnalysisResult
    :keyword bool include_fields: Whether to include extracted fields.
    :keyword bool include_markdown: Whether to include markdown body.
    :keyword metadata: Optional user-provided metadata dict.
    :paramtype metadata: dict[str, Any] or None
    :keyword bool is_multi_segment: Whether this is part of a multi-segment result.
    :returns: The rendered string with YAML front matter and optional body.
    :rtype: str
    """
    from .models import AudioVisualContent, DocumentContent

    # -- Build ordered front matter data --
    fm: Dict[str, Any] = {}

    # 1. contentType
    fm["contentType"] = content.kind or "unknown"

    # 2. User metadata
    if metadata:
        for key, value in metadata.items():
            fm[key] = value

    # 3. timeRange (audioVisual — only for multi-segment)
    if isinstance(content, AudioVisualContent) and is_multi_segment:
        if content.start_time_ms is not None and content.end_time_ms is not None:
            fm["timeRange"] = _format_time_range(
                content.start_time_ms, content.end_time_ms
            )

    # 4. category (classified documents)
    if content.category:
        fm["category"] = content.category

    # 5. pages (documents)
    pages_str = _format_pages(content)
    if pages_str is not None:
        fm["pages"] = pages_str

    # 6. fields
    if include_fields and content.fields:
        resolved = _resolve_fields(content.fields)
        if resolved:
            fm["fields"] = resolved

    # 7. rai_warnings
    if result.warnings:
        warnings_list = _format_warnings(result.warnings)
        if warnings_list:
            fm["rai_warnings"] = warnings_list

    # -- Build output string --
    front_matter = _build_front_matter(fm)

    if include_markdown and content.markdown:
        md = content.markdown
        if isinstance(content, DocumentContent):
            md = _add_page_markers(content, md)
        return front_matter + "\n" + md
    return front_matter


# ---------------------------------------------------------------------------
# Page numbering
# ---------------------------------------------------------------------------


def _add_page_markers(content: "DocumentContent", markdown: str) -> str:
    """Add ``<!-- page N -->`` markers to document markdown.

    :param content: The document content with page information.
    :type content: ~azure.ai.contentunderstanding.models.DocumentContent
    :param str markdown: The markdown text to annotate.
    :returns: The markdown with page markers inserted.
    :rtype: str
    """
    if content.pages:
        result = _page_markers_from_spans(markdown, content.pages)
        if result is not markdown:  # spans were found and used
            return result
    return _page_markers_from_breaks(markdown, content)


def _page_markers_from_spans(markdown: str, pages: "List[DocumentPage]") -> str:
    """Insert page markers using ``pages[].spans`` offsets.

    :param str markdown: The markdown text.
    :param pages: The list of document pages with span info.
    :type pages: list[~azure.ai.contentunderstanding.models.DocumentPage]
    :returns: The markdown with page markers inserted at span offsets.
    :rtype: str
    """
    markers: List[tuple] = []
    for page in pages:
        if page.spans:
            markers.append((page.spans[0].offset, page.page_number))

    if not markers:
        return markdown

    markers.sort(key=lambda m: m[0])

    # Strip existing <!-- PageBreak --> markers since page markers replace them
    cleaned = re.sub(r"\n*<!-- PageBreak -->\n*", "\n\n", markdown)

    # Compute offset shifts from the cleaning
    # Re-map original offsets to cleaned string positions
    break_pattern = re.compile(r"\n*<!-- PageBreak -->\n*")
    shifts: List[tuple] = []  # (original_pos, delta)
    for m in break_pattern.finditer(markdown):
        replacement_len = 2  # "\n\n"
        delta = m.end() - m.start() - replacement_len
        shifts.append((m.start(), delta))

    def _adjusted_offset(orig: int) -> int:
        total = 0
        for pos, delta in shifts:
            if orig > pos:
                total += delta
        return orig - total

    # Build result by splicing at page boundaries
    parts: List[str] = []
    prev = 0
    for offset, page_num in markers:
        adj = _adjusted_offset(offset)
        parts.append(cleaned[prev:adj])
        parts.append(f"<!-- page {page_num} -->\n\n")
        prev = adj
    parts.append(cleaned[prev:])

    return "".join(parts)


def _page_markers_from_breaks(markdown: str, content: "DocumentContent") -> str:
    """Fall back to splitting on ``<!-- PageBreak -->`` markers.

    :param str markdown: The markdown text.
    :param content: The document content with page number info.
    :type content: ~azure.ai.contentunderstanding.models.DocumentContent
    :returns: The markdown with page markers replacing PageBreak markers.
    :rtype: str
    """
    start_page = 1
    if content.start_page_number is not None:
        start_page = content.start_page_number

    chunks = re.split(r"\n*<!-- PageBreak -->\n*", markdown)
    parts: List[str] = []
    for i, chunk in enumerate(chunks):
        page_num = start_page + i
        text = chunk.strip()
        if text:
            parts.append(f"<!-- page {page_num} -->\n\n{text}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _format_time_range(start_ms: int, end_ms: int) -> str:
    """Format millisecond timestamps as ``MM:SS \u2013 MM:SS``.

    :param int start_ms: Start time in milliseconds.
    :param int end_ms: End time in milliseconds.
    :returns: The formatted time range string.
    :rtype: str
    """

    def _fmt(ms: int) -> str:
        total_s = ms // 1000
        return f"{total_s // 60:02d}:{total_s % 60:02d}"

    return f"{_fmt(start_ms)} \u2013 {_fmt(end_ms)}"


def _format_pages(content: "AnalysisContent") -> Any:
    """Return a pages value: int for single page, string for range, or *None*.

    :param content: The analysis content to extract page info from.
    :type content: ~azure.ai.contentunderstanding.models.AnalysisContent
    """
    from .models import DocumentContent

    if not isinstance(content, DocumentContent):
        return None
    start = content.start_page_number
    end = content.end_page_number
    if start is None or end is None:
        return None
    if start == end:
        return start
    return f"{start}-{end}"


def _format_warnings(
    warnings: "List[ODataV4Format]",
) -> List[Dict[str, str]]:
    """Convert ODataV4Format warnings to plain dicts for YAML output.

    :param warnings: The list of warnings to convert.
    :type warnings: list[~azure.ai.contentunderstanding.models.ODataV4Format]
    :returns: A list of warning dicts with code, message, and target keys.
    :rtype: list[dict[str, str]]
    """
    items: List[Dict[str, str]] = []
    for w in warnings:
        entry: Dict[str, str] = {}
        if getattr(w, "code", None):
            entry["code"] = w.code  # type: ignore[assignment, union-attr]
        if getattr(w, "message", None):
            entry["message"] = w.message  # type: ignore[assignment, union-attr]
        if getattr(w, "target", None):
            entry["target"] = w.target  # type: ignore[assignment, union-attr]
        if entry:
            items.append(entry)
    return items


# ---------------------------------------------------------------------------
# Minimal YAML serializer (no external dependency)
# ---------------------------------------------------------------------------

_YAML_SPECIAL_START = re.compile(r"^[\-\?\:\,\[\]\{\}\#\&\*\!\|\>\'\"\%\@\`]")
_YAML_SPECIAL_INSIDE = re.compile(r"[:\#] |[\n\r]")
_YAML_BOOL = re.compile(r"^(true|false|yes|no|on|off|null)$", re.IGNORECASE)
_YAML_NUMBER = re.compile(r"^[+\-]?(\d+\.?\d*|\.\d+)([eE][+\-]?\d+)?$")
_YAML_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def _yaml_scalar(value: Any) -> str:
    """Serialize a scalar to its YAML text form.

    :param value: The value to serialize.
    :type value: Any
    :returns: The YAML-formatted string.
    :rtype: str
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return str(value)
        return str(int(value)) if value == int(value) else str(value)

    s = str(value)
    needs_quote = (
        not s
        or _YAML_BOOL.match(s)
        or _YAML_NUMBER.match(s)
        or _YAML_DATE.match(s)
        or _YAML_SPECIAL_START.search(s)
        or _YAML_SPECIAL_INSIDE.search(s)
    )
    return ("'" + s.replace("'", "''") + "'") if needs_quote else s


def _build_front_matter(data: Dict[str, Any]) -> str:
    """Build a ``---`` delimited YAML front matter string.

    :param data: The data to serialize as YAML front matter.
    :type data: dict[str, Any]
    :returns: The YAML front matter string.
    :rtype: str
    """
    lines: List[str] = ["---"]
    _emit_mapping(lines, data, indent=0)
    lines.append("---")
    return "\n".join(lines)


def _emit_mapping(lines: List[str], mapping: Dict[str, Any], indent: int) -> None:
    """Emit a YAML mapping (block style).

    :param lines: The list of output lines to append to.
    :type lines: list[str]
    :param mapping: The mapping to emit.
    :type mapping: dict[str, Any]
    :param int indent: The current indentation level.
    """
    prefix = "  " * indent
    for key, value in mapping.items():
        if value is None:
            continue
        safe_key = _yaml_scalar(key)
        if isinstance(value, dict):
            if not value:
                continue
            lines.append(f"{prefix}{safe_key}:")
            _emit_mapping(lines, value, indent + 1)
        elif isinstance(value, list):
            if not value:
                continue
            lines.append(f"{prefix}{safe_key}:")
            _emit_sequence(lines, value, indent)
        else:
            lines.append(f"{prefix}{safe_key}: {_yaml_scalar(value)}")


def _emit_sequence(lines: List[str], sequence: List[Any], indent: int) -> None:
    """Emit a YAML sequence (block style, compact notation).

    :param lines: The list of output lines to append to.
    :type lines: list[str]
    :param sequence: The sequence to emit.
    :type sequence: list[Any]
    :param int indent: The current indentation level.
    """
    prefix = "  " * indent
    for item in sequence:
        if isinstance(item, dict):
            first = True
            for k, v in item.items():
                if v is None:
                    continue
                tag = f"{prefix}- " if first else f"{prefix}  "
                safe_k = _yaml_scalar(k)
                if isinstance(v, dict) and v:
                    lines.append(f"{tag}{safe_k}:")
                    _emit_mapping(lines, v, indent + 2)
                elif isinstance(v, list) and v:
                    lines.append(f"{tag}{safe_k}:")
                    inner_indent = indent + 1
                    _emit_sequence(lines, v, inner_indent)
                else:
                    lines.append(f"{tag}{safe_k}: {_yaml_scalar(v)}")
                first = False
        else:
            lines.append(f"{prefix}- {_yaml_scalar(item)}")
