# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional


class DefaultDeploymentTemplate:
    """Default deployment template reference for a model.

    :param asset_id: The asset ID of the deployment template. 
        Format: azureml://registries/{registry_name}/deploymenttemplates/{template_name}/versions/{version}
    :type asset_id: str
    """

    def __init__(
        self,
        *,
        asset_id: Optional[str] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        """Initialize DefaultDeploymentTemplate.

        :param asset_id: The asset ID of the deployment template.
        :type asset_id: Optional[str]
        """
        self.asset_id = asset_id

    def __eq__(self, other: object) -> bool:
        """Check equality based on asset_id.

        :param other: The object to compare with.
        :type other: object
        :return: True if equal, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, DefaultDeploymentTemplate):
            return NotImplemented
        return self.asset_id == other.asset_id

    def __ne__(self, other: object) -> bool:
        """Check inequality.

        :param other: The object to compare with.
        :type other: object
        :return: True if not equal, False otherwise.
        :rtype: bool
        """
        return not self.__eq__(other)

    def __repr__(self) -> str:
        """String representation.

        :return: String representation of the object.
        :rtype: str
        """
        return f"DefaultDeploymentTemplate(asset_id={self.asset_id!r})"
