# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from msrest import Deserializer, Serializer

from . import VERSION, models


class BatchTableOperations(object):
    """
    BatchTableOperations operations

    You should not instantiate this class directly. Instead, you should create a Client instance that
    instantiates it for you and attaches it as an attribute.

    :ivar models: Alias to model classes used in this operation group.
    :type models: ~azure_table.models
    :param client: Client for service requests.
    :param config: Configuration of service client.
    :param serializer: An object model serializer.
    :param deserializer: An object model deserializer.
    """

    models = models

    def __init__(self, client, config, serializer, deserializer):
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config

    def _insert_entity(
            table, # type: str
            **kwargs # type: Any
    ):
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        # Construct headers
        header_parameters = {} # type: Dict[str, Any]
        header_parameters['x-ms-version'] = 


        pass


    def _update_entity():
        pass


    def _merge_entity():
        pass


    def _delete_entity():
        pass


    def _upsert_entity():
        pass
