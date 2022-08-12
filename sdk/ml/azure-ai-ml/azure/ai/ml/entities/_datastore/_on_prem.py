# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from base64 import b64encode
from pathlib import Path
from typing import Dict, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import DatastoreData, DatastoreType
from azure.ai.ml._restclient.v2022_02_01_preview.models import HdfsDatastore as RestHdfsDatastore
from azure.ai.ml._schema._datastore._on_prem import HdfsSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.entities._datastore.utils import _from_rest_datastore_credentials_preview
from azure.ai.ml.entities._util import load_from_dict

from ._constants import HTTP
from ._on_prem_credentials import KerberosKeytabCredentials, KerberosPasswordCredentials


@experimental
class HdfsDatastore(Datastore):
    """HDFS datastore that is linked to an Azure ML workspace.

    :param name: Name of the datastore.
    :type name: str
    :param name_node_address: IP Address or DNS HostName.
    :type name_node_address: str
    :param hdfs_server_certificate: The TLS cert of the HDFS server (optional). Needs to be a local path on create and will be a base64 encoded string on get.
    :type hdfs_server_certificate: str
    :param protocol: http or https
    :type protocol: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param credentials: Credentials to use for Azure ML workspace to connect to the storage.
    :type credentials: Union[KerberosKeytabCredentials, KerberosPasswordCredentials]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        name_node_address: str,
        hdfs_server_certificate: str = None,
        protocol: str = HTTP,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        credentials: Union[KerberosKeytabCredentials, KerberosPasswordCredentials],
        **kwargs
    ):
        kwargs[TYPE] = DatastoreType.HDFS
        super().__init__(
            name=name, description=description, tags=tags, properties=properties, credentials=credentials, **kwargs
        )

        self.hdfs_server_certificate = hdfs_server_certificate
        self.name_node_address = name_node_address
        self.protocol = protocol

    def _to_rest_object(self) -> DatastoreData:
        use_this_cert = None
        if self.hdfs_server_certificate:
            with open(self.hdfs_server_certificate, "rb") as f:
                use_this_cert = b64encode(f.read()).decode("utf-8")
        hdfs_ds = RestHdfsDatastore(
            credentials=self.credentials._to_rest_object(),
            hdfs_server_certificate=use_this_cert,
            name_node_address=self.name_node_address,
            protocol=self.protocol,
            description=self.description,
            tags=self.tags,
        )
        return DatastoreData(properties=hdfs_ds)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "HdfsDatastore":
        return load_from_dict(HdfsSchema, data, context, additional_message)

    @classmethod
    def _from_rest_object(cls, datastore_resource: DatastoreData):
        properties: RestHdfsDatastore = datastore_resource.properties
        return HdfsDatastore(
            name=datastore_resource.name,
            id=datastore_resource.id,
            credentials=_from_rest_datastore_credentials_preview(properties.credentials),
            hdfs_server_certificate=properties.hdfs_server_certificate,
            name_node_address=properties.name_node_address,
            protocol=properties.protocol,
            description=properties.description,
            tags=properties.tags,
        )

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.hdfs_server_certificate == other.hdfs_server_certificate
            and self.name_node_address == other.name_node_address
            and self.protocol == other.protocol
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def _to_dict(self) -> Dict:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return HdfsSchema(context=context).dump(self)
