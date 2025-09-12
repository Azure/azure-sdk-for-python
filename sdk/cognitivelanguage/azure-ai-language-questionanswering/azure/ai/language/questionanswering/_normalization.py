"""Internal normalization helpers (shared by sync/async patches).

Handles mapping of user-friendly snake_case and Pythonic inputs into service payload shape.
Not part of the public surface; subject to change without notice.
"""
from __future__ import annotations
from typing import Any, Mapping, Optional

__all__ = [
    "_normalize_text_options",
    "_normalize_answers_dict",
]

def _normalize_text_options(raw: Mapping[str, Any], default_lang: Optional[str]) -> dict[str, Any]:
    """Normalize mapping provided to get_answers_from_text.

    Handles:
      - text_documents -> records
      - list[str] -> list[{id,text}]
      - inject language from client default
    """
    opts: dict[str, Any] = dict(raw)
    if "records" not in opts and "text_documents" in opts:
        opts["records"] = opts.pop("text_documents")
    recs = opts.get("records")
    if isinstance(recs, list) and any(isinstance(x, str) for x in recs):
        opts["records"] = [
            {"id": str(i), "text": v} if isinstance(v, str) else v for i, v in enumerate(recs)
        ]
    if "language" not in opts and default_lang:
        opts["language"] = default_lang
    return opts


def _normalize_answers_dict(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize mapping provided to get_answers into service-ready payload.

    Includes:
      - top-level snake_case aliases -> camelCase
      - answer_context -> context (with nested previous_* aliases)
      - short_answer_options -> answerSpanRequest
      - filters normalization (metadata_filter, logical_operation, tuples)
    """
    opts: dict[str, Any] = dict(raw)

    def _pop_map(src: str, dst: str) -> None:
        if src in opts and dst not in opts:
            opts[dst] = opts.pop(src)

    # Top-level aliases
    _pop_map("qna_id", "qnaId")
    _pop_map("user_id", "userId")
    _pop_map("confidence_threshold", "confidenceScoreThreshold")
    _pop_map("include_unstructured_sources", "includeUnstructuredSources")
    _pop_map("ranker_kind", "rankerKind")

    # answer_context
    if "answer_context" in opts and "context" not in opts:
        ctx = opts.pop("answer_context")
        if isinstance(ctx, Mapping):
            ctx_dict: dict[str, Any] = dict(ctx)  # type: ignore[arg-type]
            if "previous_user_query" in ctx_dict and "previousUserQuery" not in ctx_dict:
                ctx_dict["previousUserQuery"] = ctx_dict.pop("previous_user_query")
            if "previous_question" in ctx_dict and "previousUserQuery" not in ctx_dict:
                ctx_dict["previousUserQuery"] = ctx_dict.pop("previous_question")
            if "previous_qna_id" in ctx_dict and "previousQnaId" not in ctx_dict:
                ctx_dict["previousQnaId"] = ctx_dict.pop("previous_qna_id")
            opts["context"] = ctx_dict
        else:
            prev_q = getattr(ctx, "previous_user_query", None) or getattr(ctx, "previous_question", None)
            prev_id = getattr(ctx, "previous_qna_id", None)
            ctx_out: dict[str, Any] = {}
            if prev_q is not None:
                ctx_out["previousUserQuery"] = prev_q
            if prev_id is not None:
                ctx_out["previousQnaId"] = prev_id
            if ctx_out:
                opts["context"] = ctx_out

    # short_answer_options
    if "short_answer_options" in opts and "answerSpanRequest" not in opts:
        sao = opts.pop("short_answer_options")
        if isinstance(sao, Mapping):
            sao_dict = dict(sao)  # type: ignore[arg-type]
        else:
            sao_dict = {k: getattr(sao, k) for k in ("confidence_threshold", "top") if hasattr(sao, k)}
        asr: dict[str, Any] = {"enable": True}
        if "confidence_threshold" in sao_dict:
            asr["confidenceScoreThreshold"] = sao_dict.get("confidence_threshold")
        if "top" in sao_dict:
            asr["topAnswersWithSpan"] = sao_dict.get("top")
        opts["answerSpanRequest"] = asr

    # filters
    if "filters" in opts and isinstance(opts["filters"], Mapping):
        flt = dict(opts["filters"])  # type: ignore[arg-type]
        if "metadata_filter" in flt and "metadataFilter" not in flt:
            flt["metadataFilter"] = flt.pop("metadata_filter")
        if "metadataFilter" in flt and isinstance(flt["metadataFilter"], Mapping):
            mf = dict(flt["metadataFilter"])  # type: ignore[arg-type]
            if "logical_operation" in mf and "logicalOperation" not in mf:
                val = str(mf.pop("logical_operation") or "").upper()
                if val in ("OR", "AND"):
                    mf["logicalOperation"] = val
                else:
                    mf["logicalOperation"] = val  # let service decide invalid value
            elif "logicalOperation" in mf and isinstance(mf["logicalOperation"], str):
                mf["logicalOperation"] = mf["logicalOperation"].upper()
            if "metadata" in mf and isinstance(mf["metadata"], list):
                new_meta: list[Any] = []
                for item in mf["metadata"]:
                    if isinstance(item, tuple) and len(item) == 2:
                        new_meta.append({"key": item[0], "value": item[1]})
                    else:
                        new_meta.append(item)
                mf["metadata"] = new_meta
            flt["metadataFilter"] = mf
        opts["filters"] = flt

    return opts
