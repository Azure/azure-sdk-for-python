# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Wire adapters for the Decision protocols that the shared runner speaks.

Evaluators always build one canonical request: evidence (``state``) and ``noul`` or ``score`` questions keyed by
identifier. A protocol translates that request to its provider's wire contract and binds the provider's answers back
to the same identifiers in the canonical answer shape. Protocols never validate answer values, score, apply
thresholds or decide applicability: values are validated only when an evaluator reads them, so an answer that an
evaluation does not use cannot fail it.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping
from urllib.parse import urlsplit

REFUSAL = "refusal"


class DecisionProtocol(ABC):
    """Translates canonical Decision requests and responses for one provider contract."""

    name: str
    supports_refusals = False

    @abstractmethod
    def operation_url(self, endpoint: str) -> str:
        """Return the provider operation URL for a validated account endpoint.

        :param endpoint: The account endpoint from the model configuration.
        :type endpoint: str
        :return: The URL that receives the request.
        :rtype: str
        :raises ValueError: If the endpoint path is not supported by this protocol.
        """

    @abstractmethod
    def encode(self, deployment: str, state: Any, questions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Return the wire request body for canonical evidence and questions.

        :param deployment: The deployment name sent as the request's model.
        :type deployment: str
        :param state: The prepared evidence, as text or data that the runner has already checked is finite JSON.
        :type state: Any
        :param questions: Canonical ``noul`` and ``score`` questions keyed by identifier.
        :type questions: Dict[str, Dict[str, Any]]
        :return: The request body.
        :rtype: Dict[str, Any]
        :raises ValueError: If the provider cannot express the questions.
        """

    @abstractmethod
    def bind_answers(self, payload: Dict[str, Any], questions: Mapping[str, Any]) -> Dict[str, Any]:
        """Bind the provider's answers to question identifiers in the canonical answer shape.

        :param payload: The provider response.
        :type payload: Dict[str, Any]
        :param questions: The canonical questions keyed by identifier.
        :type questions: Mapping[str, Any]
        :return: Answers keyed by question identifier.
        :rtype: Dict[str, Any]
        :raises ValueError: If the answers cannot be bound to the questions.
        """


class MicrosoftDecisionProtocol(DecisionProtocol):
    """The Microsoft Decision contract, which is also the canonical shape. A supplied endpoint path is kept."""

    name = "microsoft"
    _PATH = "/providers/microsoft/v1/systemone"

    def operation_url(self, endpoint: str) -> str:
        return f"{endpoint.rstrip('/')}{self._PATH}"

    def encode(self, deployment: str, state: Any, questions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        return {"model": deployment, "state": state, "questions": questions}

    def bind_answers(self, payload: Dict[str, Any], questions: Mapping[str, Any]) -> Dict[str, Any]:
        answers = payload.get("answers")
        if not isinstance(answers, dict):
            raise ValueError("answers are missing.")
        return answers


class OpenAIDecisionProtocol(DecisionProtocol):
    """Azure OpenAI Decisions: predicates, ordered score levels and named answers that may be refused.

    A ``noul`` question becomes a ``predicate`` whose instructions also state its true and false criteria, and a
    ``score`` question's criteria become levels labeled ``"Level 1"`` to ``"Level n"`` from the lowest, the ordinal
    names rubric text such as "imply level 2" uses. Structured evidence is sent as compact JSON text. For example, the
    answer ``{"name": "status", "type": "predicate", "probability": 0.9}`` binds to ``{"type": "noul", "noul": 0.9}``
    for question ``status``, and a score's level probabilities become a map keyed by the provider's zero-based level
    index. A refused question binds to ``{"type": "refusal"}``.
    """

    name = "openai"
    supports_refusals = True
    MAX_QUESTIONS = 400
    _BASE_PATHS = ("", "/openai", "/openai/v1")

    def operation_url(self, endpoint: str) -> str:
        parsed = urlsplit(endpoint)
        if parsed.path.rstrip("/") not in self._BASE_PATHS:
            raise ValueError("OpenAI Decisions requires an account endpoint or its /openai/v1 base URL.")
        return f"{parsed.scheme}://{parsed.netloc}/openai/v1/decisions"

    def encode(self, deployment: str, state: Any, questions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        if not 1 <= len(questions) <= self.MAX_QUESTIONS:
            raise ValueError(f"OpenAI Decisions requires between 1 and {self.MAX_QUESTIONS} questions.")
        evidence = (
            state
            if isinstance(state, str)
            else json.dumps(state, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        )
        encoded = [self._encode_question(name, question) for name, question in questions.items()]
        return {"model": deployment, "input": evidence, "questions": encoded}

    @staticmethod
    def _encode_question(name: str, question: Dict[str, Any]) -> Dict[str, Any]:
        instructions = question.get("instructions")
        if not isinstance(instructions, str) or not instructions.strip():
            raise ValueError("Decision questions require nonempty text instructions.")
        criteria = question.get("criteria")
        if question["type"] == "noul":
            if criteria is not None:
                if (
                    not isinstance(criteria, dict)
                    or set(criteria) != {"true", "false"}
                    or not all(isinstance(value, str) and value.strip() for value in criteria.values())
                ):
                    raise ValueError("Boolean criteria must describe both 'true' and 'false'.")
                instructions += (
                    f"\n\nThe predicate is true when: {criteria['true']}"
                    f"\nThe predicate is false when: {criteria['false']}"
                )
            return {"name": name, "type": "predicate", "instructions": instructions}
        if (
            not isinstance(criteria, list)
            or not 2 <= len(criteria) <= 10
            or not all(isinstance(value, str) and value.strip() for value in criteria)
        ):
            raise ValueError("OpenAI score questions require 2 to 10 ordered text criteria.")
        levels = [
            {"label": f"Level {position}", "description": description}
            for position, description in enumerate(criteria, start=1)
        ]
        return {"name": name, "type": "score", "instructions": instructions, "levels": levels}

    def bind_answers(self, payload: Dict[str, Any], questions: Mapping[str, Any]) -> Dict[str, Any]:
        answers = payload.get("answers")
        if not isinstance(answers, list):
            raise ValueError("answers are missing.")
        bound: Dict[str, Any] = {}
        for answer in answers:
            name = answer.get("name") if isinstance(answer, dict) else None
            if not isinstance(name, str) or name not in questions or name in bound:
                raise ValueError("answer names must match each question exactly once.")
            bound[name] = self._canonical_answer(answer)
        return bound

    @staticmethod
    def _canonical_answer(answer: Dict[str, Any]) -> Dict[str, Any]:
        kind = answer.get("type")
        if kind == "predicate":
            return {"type": "noul", "noul": answer.get("probability")}
        if kind == "score":
            return {
                "type": "score",
                "score": answer.get("score"),
                "confidence": answer.get("confidence"),
                "probabilities": _level_probabilities(answer.get("probabilities")),
            }
        # A refusal, or an unexpected type that the runner rejects against its question.
        return {"type": kind}


def _level_probabilities(distribution: Any) -> Any:
    """Key each level's probability by its index; a malformed list is kept as is and fails when it is read."""
    if not isinstance(distribution, list):
        return distribution
    probabilities: Dict[str, Any] = {}
    for item in distribution:
        index = item.get("value") if isinstance(item, dict) else None
        if isinstance(index, bool) or not isinstance(index, int) or str(index) in probabilities:
            return distribution
        probabilities[str(index)] = item.get("probability")
    return probabilities


DECISION_PROTOCOLS: Dict[str, DecisionProtocol] = {
    protocol.name: protocol for protocol in (MicrosoftDecisionProtocol(), OpenAIDecisionProtocol())
}
