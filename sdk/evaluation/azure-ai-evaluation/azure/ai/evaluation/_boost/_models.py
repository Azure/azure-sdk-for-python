from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class _EvaluationCase:
    """Represents a single evaluation case with metrics."""

    case_id: str
    metrics: Dict[str, Any]
    conversation: List[Dict[str, Any]]

    @classmethod
    def from_row(cls, row: Dict, case_id: str) -> "_EvaluationCase":
        """Create from evaluation result row."""
        metrics = cls._extract_metrics(row)
        conversation = row.get("inputs.conversation", {}).get("messages", [])
        return cls(case_id=case_id, metrics=metrics, conversation=conversation)

    @staticmethod
    def _extract_metrics(row: Dict) -> Dict[str, Any]:
        """Extract evaluation metrics and reasons from evaluation row.
        
        Extracts all outputs from evaluators, including numeric scores,
        pass/fail results, thresholds, and reasoning explanations.
        """
        metrics = {}
        for key, value in row.items():
            if key.startswith("outputs."):
                metric_name = key.replace("outputs.", "")
                metrics[metric_name] = value
        return metrics
