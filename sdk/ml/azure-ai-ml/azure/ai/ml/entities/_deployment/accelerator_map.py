# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._utils._experimental import experimental


@experimental
class AcceleratorMap:
    """Accelerator map for a deployment template, describing the accelerator type
    and how many accelerators are needed per model instance.

    :param accelerator_type: The type of accelerator (e.g. "H100_80GB", "H200_141GB", "A100_80GB").
    :type accelerator_type: str
    :param number_of_accelerators_per_model_instance: Number of accelerators per model instance.
    :type number_of_accelerators_per_model_instance: int
    :param default: Whether this is the default accelerator map for the deployment template.
    :type default: bool
    """

    def __init__(  # pylint: disable=name-too-long
        self,
        *,
        accelerator_type: str,
        number_of_accelerators_per_model_instance: int,
        default: Optional[bool] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        self.accelerator_type = accelerator_type
        self.number_of_accelerators_per_model_instance = number_of_accelerators_per_model_instance
        self.default = default

    def _to_rest_dict(self) -> dict:
        """Convert to REST API dictionary.

        :return: Dictionary with camelCase keys for REST API.
        :rtype: dict
        """
        result = {
            "acceleratorType": self.accelerator_type,
            "numberOfAcceleratorsPerModelInstance": self.number_of_accelerators_per_model_instance,
        }
        if self.default is not None:
            result["default"] = self.default
        return result

    @classmethod
    def _from_rest_dict(cls, data: dict) -> "AcceleratorMap":
        """Create AcceleratorMap from REST API dictionary.

        :param data: REST dictionary with camelCase keys.
        :type data: dict
        :return: AcceleratorMap instance.
        :rtype: AcceleratorMap
        """
        return cls(
            accelerator_type=data.get("acceleratorType", ""),
            number_of_accelerators_per_model_instance=data.get("numberOfAcceleratorsPerModelInstance", 0),
            default=data.get("default"),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AcceleratorMap):
            return NotImplemented
        return (
            self.accelerator_type == other.accelerator_type
            and self.number_of_accelerators_per_model_instance == other.number_of_accelerators_per_model_instance
            and self.default == other.default
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self) -> str:
        return (
            f"AcceleratorMap(accelerator_type={self.accelerator_type!r}, "
            f"number_of_accelerators_per_model_instance={self.number_of_accelerators_per_model_instance!r}, "
            f"default={self.default!r})"
        )
