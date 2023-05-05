# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------


from azure.ai.ml._restclient.v2023_04_01_preview.models import ModelConfiguration as RestModelConfiguration
from azure.ai.ml._utils._experimental import experimental


@experimental
class ModelConfiguration:
    """ModelConfiguration.

    :param mode: The mode of the model.
    :type mode: str
    :param mount_path: The mount path of the model.
    :type mount_path: str
    """

    def __init__(self, *, mode: str = None, mount_path: str = None):
        self.mode = mode
        self.mount_path = mount_path

    @classmethod
    def _from_rest_object(cls, rest_obj: RestModelConfiguration) -> "ModelConfiguration":
        return ModelConfiguration(mode=rest_obj.mode, mount_path=rest_obj.mount_path)

    def _to_rest_object(self) -> RestModelConfiguration:
        return RestModelConfiguration(mode=self.mode, mount_path=self.mount_path)
