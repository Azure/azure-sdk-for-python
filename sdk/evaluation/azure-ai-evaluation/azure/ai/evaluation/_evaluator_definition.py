from abc import ABC
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class EvaluatorMetric:
    type: str = "ordinal"
    desirable_direction: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type}
        if self.desirable_direction is not None:
            result["desirable_direction"] = self.desirable_direction
        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluatorMetric":
        return cls(
            type=data.get("type", "ordinal"),
            desirable_direction=data.get("desirable_direction"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
        )


@dataclass
class ObjectParameterDescriptorWithRequired:
    required: List[str] = field(default_factory=list)
    type: str = "object"
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"required": self.required, "type": self.type, "properties": self.properties}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectParameterDescriptorWithRequired":
        return cls(
            required=data.get("required", []), type=data.get("type", "object"), properties=data.get("properties", {})
        )


class EvaluatorDefinition(ABC):
    """Base class for evaluator definitions"""

    def __init__(self):
        self.init_parameters: ObjectParameterDescriptorWithRequired = ObjectParameterDescriptorWithRequired()
        self.metrics: Dict[str, EvaluatorMetric] = {}
        self.data_schema: ObjectParameterDescriptorWithRequired = ObjectParameterDescriptorWithRequired()
        self.type: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "init_parameters": self.init_parameters.to_dict(),
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "data_schema": self.data_schema.to_dict(),
        }
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluatorDefinition":
        # Create a generic instance since specific subclasses are not defined
        instance = cls.__new__(cls)
        instance.__init__()

        instance.init_parameters = ObjectParameterDescriptorWithRequired.from_dict(data.get("init_parameters", {}))
        instance.metrics = {k: EvaluatorMetric.from_dict(v) for k, v in data.get("metrics", {}).items()}
        instance.data_schema = ObjectParameterDescriptorWithRequired.from_dict(data.get("data_schema", {}))
        return instance
