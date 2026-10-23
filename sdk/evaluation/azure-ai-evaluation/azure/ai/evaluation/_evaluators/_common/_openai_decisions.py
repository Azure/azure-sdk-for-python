# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Translate the shared Decision rubric contract to Azure OpenAI Decisions.

Scoring remains the responsibility of the existing evaluator strategies. In particular,
the provider's probability-weighted score is not an ordinal evaluation score.
"""

import json
import math
from typing import Any, Dict


def encode_request(state: Any, questions: Dict[str, Dict[str, Any]], deployment: str) -> Dict[str, Any]:
    """Encode text/structured evidence and named Boolean or ordinal questions."""
    if not isinstance(questions, dict) or not 1 <= len(questions) <= 400:
        raise ValueError("OpenAI Decisions requires between 1 and 400 questions.")
    encoded = []
    for name, question in questions.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(question, dict):
            raise ValueError("Decision questions require nonempty string names and object definitions.")
        instructions = question.get("instructions")
        if not isinstance(instructions, str) or not instructions.strip():
            raise ValueError("Decision questions require nonempty text instructions.")
        kind = question.get("type")
        criteria = question.get("criteria")
        item = {"name": name, "instructions": instructions}
        if kind == "noul":
            item["type"] = "predicate"
            if criteria is not None:
                if (
                    not isinstance(criteria, dict)
                    or set(criteria) != {"true", "false"}
                    or not all(isinstance(value, str) and value.strip() for value in criteria.values())
                ):
                    raise ValueError("Boolean criteria must describe both 'true' and 'false'.")
                item["instructions"] += (
                    f"\n\nThe predicate is true when: {criteria['true']}"
                    f"\nThe predicate is false when: {criteria['false']}"
                )
        elif kind == "score":
            if (
                not isinstance(criteria, list)
                or not 2 <= len(criteria) <= 10
                or not all(isinstance(value, str) and value.strip() for value in criteria)
            ):
                raise ValueError("OpenAI score questions require 2 to 10 ordered text criteria.")
            item.update(
                type="score",
                levels=[
                    {"label": str(index), "description": description} for index, description in enumerate(criteria)
                ],
            )
        else:
            raise ValueError("OpenAI evaluation supports Boolean and score questions.")
        encoded.append(item)
    evidence = (
        state
        if isinstance(state, str)
        else json.dumps(state, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    )
    return {"model": deployment, "input": evidence, "questions": encoded}


def _probability(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError("OpenAI answer probabilities must be finite numbers between zero and one.")
    return float(value)


def decode_response(payload: Any, questions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize named answers while retaining their original protocol and representation.

    A refusal fails the evaluation explicitly, including a partially refused bundle. The
    caller retains known request usage on the error; no zero score or skipped dimension is fabricated.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("answers"), list):
        raise ValueError("OpenAI Decisions answers must be an array.")
    answers = {}
    for answer in payload["answers"]:
        if not isinstance(answer, dict) or not isinstance(answer.get("name"), str):
            raise ValueError("OpenAI Decisions answers require question names.")
        name = answer["name"]
        if name not in questions or name in answers:
            raise ValueError("OpenAI Decisions answer names must match each question exactly once.")
        answers[name] = answer
    if set(answers) != set(questions):
        raise ValueError("OpenAI Decisions answers are missing questions.")
    normalized = {}
    for name, question in questions.items():
        answer = answers[name]
        kind = answer.get("type")
        if kind == "refusal":
            raise ValueError("OpenAI Decisions refused an evaluation question; no score is available.")
        if question["type"] == "noul" and kind == "predicate":
            normalized[name] = {"type": "noul", "noul": _probability(answer.get("probability"))}
        elif question["type"] == "score" and kind == "score":
            levels = len(question["criteria"])
            distribution = answer.get("probabilities")
            if not isinstance(distribution, list) or len(distribution) != levels:
                raise ValueError("OpenAI score distributions must contain every level exactly once.")
            probabilities = {}
            for item in distribution:
                if not isinstance(item, dict):
                    raise ValueError("OpenAI score probabilities must be objects.")
                index = item.get("value")
                if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < levels:
                    raise ValueError("OpenAI score probability values must be valid level indices.")
                if str(index) in probabilities or item.get("label") != str(index):
                    raise ValueError("OpenAI score levels must have unique indices and their requested labels.")
                probabilities[str(index)] = _probability(item.get("probability"))
            if not math.isclose(math.fsum(probabilities.values()), 1.0, rel_tol=0, abs_tol=0.001):
                raise ValueError("OpenAI score probabilities must sum to one.")
            score = answer.get("score")
            if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= levels - 1:
                raise ValueError("OpenAI score must be a finite, zero-based level mean.")
            normalized[name] = {
                "type": "score",
                "score": score,
                "confidence": _probability(answer.get("confidence")),
                "probabilities": probabilities,
            }
        else:
            raise ValueError("OpenAI Decisions answer type does not match its question.")
        normalized[name]["_native_answer"] = dict(answer)
    return {**payload, "answers": normalized}


def usage_details(usage: Any) -> Dict[str, Any]:
    """Keep known nonnegative cache/reasoning counters without duplicating token totals."""
    details = {}
    if not isinstance(usage, dict):
        return details
    for group, fields in (
        ("input_tokens_details", ("cached_tokens", "cache_write_tokens")),
        ("output_tokens_details", ("reasoning_tokens",)),
    ):
        values = usage.get(group)
        if isinstance(values, dict):
            known = {
                name: values[name]
                for name in fields
                if isinstance(values.get(name), int) and not isinstance(values[name], bool) and values[name] >= 0
            }
            if known:
                details[group] = known
    return details
