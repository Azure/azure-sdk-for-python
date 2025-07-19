from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class _EvaluationCase:
    """Represents a single evaluation case with scores."""

    case_id: str
    scores: Dict[str, float]
    conversation: List[Dict[str, Any]]

    @classmethod
    def from_row(cls, row: Dict, case_id: str) -> "_EvaluationCase":
        """Create from evaluation result row."""
        scores = cls._extract_scores(row)
        conversation = row.get("inputs.conversation", {}).get("messages", [])
        return cls(case_id=case_id, scores=scores, conversation=conversation)

    @staticmethod
    def _extract_scores(row: Dict) -> Dict[str, float]:
        """Extract numeric scores from evaluation row."""
        scores = {}
        for key, value in row.items():
            if key.startswith("outputs.") and isinstance(value, (int, float)):
                metric_name = key.replace("outputs.", "")
                scores[metric_name] = float(value)
        return scores
