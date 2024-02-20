# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------


from azure.ai.ml._restclient.v2023_08_01_preview.models import ModelConfiguration as RestModelConfiguration
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import snake_to_camel


@experimental
class ModelConfiguration:
    """ModelConfiguration.

    :param mode: The mode of the model. Possible values include: "Copy", "Download".
    :type mode: str
    :param mount_path: The mount path of the model.
    :type mount_path: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START model_configuration_entity_create]
            :end-before: [END model_configuration_entity_create]
            :language: python
            :dedent: 8
            :caption: Creating a Model Configuration object.
    """

    def __init__(self, *, mode: str = None, mount_path: str = None):
        self.mode = mode
        self.mount_path = mount_path

    @classmethod
    def _from_rest_object(cls, rest_obj: RestModelConfiguration) -> "ModelConfiguration":
        return ModelConfiguration(mode=rest_obj.mode, mount_path=rest_obj.mount_path)

    def _to_rest_object(self) -> RestModelConfiguration:
        return RestModelConfiguration(mode=snake_to_camel(self.mode), mount_path=self.mount_path)
