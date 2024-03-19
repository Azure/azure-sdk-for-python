# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,redefined-builtin,arguments-renamed

from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import Datastore as DatastoreData
from azure.ai.ml._restclient.v2023_04_01_preview.models import DatastoreType
from azure.ai.ml._utils.utils import camel_to_snake, dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, CommonYamlFields
from azure.ai.ml.entities._credentials import (
    AccountKeyConfiguration,
    CertificateConfiguration,
    NoneCredentialConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import find_type_in_override
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


class Datastore(Resource, RestTranslatableMixin, ABC):
    """Datastore of an Azure ML workspace, abstract class.

    :param name: Name of the datastore.
    :type name: str
    :param description: Description of the resource.
    :type description: str
    :param credentials: Credentials to use for Azure ML workspace to connect to the storage.
    :type credentials: Optional[Union[
        ~azure.ai.ml.entities.ServicePrincipalConfiguration,
        ~azure.ai.ml.entities.CertificateConfiguration,
        ~azure.ai.ml.entities.NoneCredentialConfiguration,
        ~azure.ai.ml.entities.AccountKeyConfiguration,
        ~azure.ai.ml.entities.SasTokenConfiguration

        ]]
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        credentials: Optional[
            Union[
                ServicePrincipalConfiguration,
                CertificateConfiguration,
                NoneCredentialConfiguration,
                AccountKeyConfiguration,
                SasTokenConfiguration,
            ]
        ],
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ):
        self._type: str = kwargs.pop("type", None)
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )

        self.credentials = NoneCredentialConfiguration() if credentials is None else credentials

    @property
    def type(self) -> str:
        return self._type

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the datastore content into a file in yaml format.

        :param dest: The destination to receive this datastore's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, **kwargs)

    @abstractmethod
    def _to_dict(self) -> Dict:
        pass

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Datastore":
        data = data or {}
        params_override = params_override or []

        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        from azure.ai.ml.entities import (
            AzureBlobDatastore,
            AzureDataLakeGen1Datastore,
            AzureDataLakeGen2Datastore,
            AzureFileDatastore,
            OneLakeDatastore,
        )

        # from azure.ai.ml.entities._datastore._on_prem import (
        #     HdfsDatastore
        # )

        ds_type: Any = None
        type_in_override = find_type_in_override(params_override)
        type = type_in_override or data.get(
            CommonYamlFields.TYPE, DatastoreType.AZURE_BLOB
        )  # override takes the priority

        # yaml expects snake casing, while service side constants are camel casing
        if type == camel_to_snake(DatastoreType.AZURE_BLOB):
            ds_type = AzureBlobDatastore
        elif type == camel_to_snake(DatastoreType.AZURE_FILE):
            ds_type = AzureFileDatastore
        elif type == camel_to_snake(DatastoreType.AZURE_DATA_LAKE_GEN1):
            ds_type = AzureDataLakeGen1Datastore
        elif type == camel_to_snake(DatastoreType.AZURE_DATA_LAKE_GEN2):
            ds_type = AzureDataLakeGen2Datastore
        elif type == camel_to_snake(DatastoreType.ONE_LAKE):
            ds_type = OneLakeDatastore
        # disable unless preview release
        # elif type == camel_to_snake(DatastoreTypePreview.HDFS):
        #    ds_type = HdfsDatastore
        else:
            msg = f"Unsupported datastore type: {type}."
            raise ValidationException(
                message=msg,
                error_type=ValidationErrorType.INVALID_VALUE,
                target=ErrorTarget.DATASTORE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        res: Datastore = ds_type._load_from_dict(
            data=data,
            context=context,
            additional_message="If the datastore type is incorrect, change the 'type' property.",
            **kwargs,
        )
        return res

    @classmethod
    def _from_rest_object(cls, datastore_resource: DatastoreData) -> "Datastore":
        from azure.ai.ml.entities import (
            AzureBlobDatastore,
            AzureDataLakeGen1Datastore,
            AzureDataLakeGen2Datastore,
            AzureFileDatastore,
            OneLakeDatastore,
        )

        # from azure.ai.ml.entities._datastore._on_prem import (
        #     HdfsDatastore
        # )

        datastore_type = datastore_resource.properties.datastore_type
        if datastore_type == DatastoreType.AZURE_DATA_LAKE_GEN1:
            res_adl_gen1: Datastore = AzureDataLakeGen1Datastore._from_rest_object(datastore_resource)
            return res_adl_gen1
        if datastore_type == DatastoreType.AZURE_DATA_LAKE_GEN2:
            res_adl_gen2: Datastore = AzureDataLakeGen2Datastore._from_rest_object(datastore_resource)
            return res_adl_gen2
        if datastore_type == DatastoreType.AZURE_BLOB:
            res_abd: Datastore = AzureBlobDatastore._from_rest_object(datastore_resource)
            return res_abd
        if datastore_type == DatastoreType.AZURE_FILE:
            res_afd: Datastore = AzureFileDatastore._from_rest_object(datastore_resource)
            return res_afd
        if datastore_type == DatastoreType.ONE_LAKE:
            res_old: Datastore = OneLakeDatastore._from_rest_object(datastore_resource)
            return res_old
        # disable unless preview release
        # elif datastore_type == DatastoreTypePreview.HDFS:
        #     return HdfsDatastore._from_rest_object(datastore_resource)
        msg = f"Unsupported datastore type {datastore_resource.properties.contents.type}"
        raise ValidationException(
            message=msg,
            error_type=ValidationErrorType.INVALID_VALUE,
            target=ErrorTarget.DATASTORE,
            no_personal_data_message=msg,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )

    @classmethod
    @abstractmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "Datastore":
        pass

    def __eq__(self, other: Any) -> bool:
        res: bool = self.name == other.name and self.type == other.type and self.credentials == other.credentials
        return res

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
