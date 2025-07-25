from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class _EvaluationCase:
    """Represents a single evaluation case with metrics."""

    case_id: str
    metrics: Dict[str, float]
    conversation: List[Dict[str, Any]]

    @classmethod
    def from_row(cls, row: Dict, case_id: str) -> "_EvaluationCase":
        """Create from evaluation result row."""
        metrics = cls._extract_metrics(row)
        conversation = row.get("inputs.conversation", {}).get("messages", [])
        return cls(case_id=case_id, metrics=metrics, conversation=conversation)

    @staticmethod
    def _extract_metrics(row: Dict) -> Dict[str, float]:
        """Extract numeric metrics from evaluation row."""
        metrics = {}
        for key, value in row.items():
            if key.startswith("outputs.") and isinstance(value, (int, float)):
                metric_name = key.replace("outputs.", "")
                metrics[metric_name] = float(value)
        return metrics
