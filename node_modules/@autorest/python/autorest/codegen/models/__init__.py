# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from typing import Any, Dict, Union
from .base import BaseModel
from .base_builder import BaseBuilder, ParameterListType
from .code_model import CodeModel
from .client import Client
from .model_type import ModelType, JSONModelType, DPGModelType, MsrestModelType
from .dictionary_type import DictionaryType
from .list_type import ListType
from .combined_type import CombinedType
from .primitive_types import (
    ByteArraySchema,
    DateType,
    DatetimeType,
    DurationType,
    IntegerType,
    FloatType,
    StringType,
    TimeType,
    AnyType,
    PrimitiveType,
    BinaryType,
    BooleanType,
    AnyObjectType,
    UnixTimeType,
    AzureCoreType,
)
from .enum_type import EnumType
from .base import BaseType
from .constant_type import ConstantType
from .imports import FileImport, ImportType, TypingSection
from .lro_operation import LROOperation
from .paging_operation import PagingOperation
from .parameter import (
    Parameter,
    ParameterMethodLocation,
    ParameterLocation,
    BodyParameter,
    ParameterDelimeter,
    MultipartBodyParameter,
    ClientParameter,
    ConfigParameter,
)
from .operation import Operation
from .property import Property
from .operation_group import OperationGroup
from .response import Response
from .parameter_list import (
    ParameterList,
    ClientGlobalParameterList,
    ConfigGlobalParameterList,
)
from .request_builder import (
    RequestBuilder,
    OverloadedRequestBuilder,
    RequestBuilderBase,
)
from .lro_paging_operation import LROPagingOperation
from .request_builder_parameter import (
    RequestBuilderParameter,
    RequestBuilderBodyParameter,
)
from .credential_types import (
    TokenCredentialType,
    AzureKeyCredentialType,
    ARMChallengeAuthenticationPolicyType,
    BearerTokenCredentialPolicyType,
    AzureKeyCredentialPolicyType,
    CredentialType,
)

__all__ = [
    "AzureKeyCredentialPolicyType",
    "AnyType",
    "BaseModel",
    "BaseType",
    "CodeModel",
    "Client",
    "ConstantType",
    "ModelType",
    "DictionaryType",
    "ListType",
    "EnumType",
    "FileImport",
    "ImportType",
    "TypingSection",
    "PrimitiveType",
    "LROOperation",
    "Operation",
    "PagingOperation",
    "Parameter",
    "ParameterList",
    "OperationGroup",
    "Property",
    "RequestBuilder",
    "Response",
    "TokenCredentialType",
    "LROPagingOperation",
    "BaseBuilder",
    "RequestBuilderParameter",
    "BinaryType",
    "ClientGlobalParameterList",
    "ConfigGlobalParameterList",
    "ParameterMethodLocation",
    "ParameterLocation",
    "OverloadedRequestBuilder",
    "RequestBuilderBase",
    "BodyParameter",
    "RequestBuilderBodyParameter",
    "ParameterDelimeter",
    "MultipartBodyParameter",
    "CredentialType",
    "ClientParameter",
    "ConfigParameter",
    "ParameterListType",
]

TYPE_TO_OBJECT = {
    "integer": IntegerType,
    "float": FloatType,
    "string": StringType,
    "list": ListType,
    "dict": DictionaryType,
    "constant": ConstantType,
    "enum": EnumType,
    "binary": BinaryType,
    "any": AnyType,
    "datetime": DatetimeType,
    "time": TimeType,
    "duration": DurationType,
    "date": DateType,
    "bytes": ByteArraySchema,
    "boolean": BooleanType,
    "combined": CombinedType,
    "OAuth2": TokenCredentialType,
    "Key": AzureKeyCredentialType,
    "ARMChallengeAuthenticationPolicy": ARMChallengeAuthenticationPolicyType,
    "BearerTokenCredentialPolicy": BearerTokenCredentialPolicyType,
    "AzureKeyCredentialPolicy": AzureKeyCredentialPolicyType,
    "any-object": AnyObjectType,
    "unixtime": UnixTimeType,
    "credential": StringType,
    "azurecore": AzureCoreType,
}
_LOGGER = logging.getLogger(__name__)


def build_type(yaml_data: Dict[str, Any], code_model: CodeModel) -> BaseType:
    yaml_id = id(yaml_data)
    try:
        return code_model.lookup_type(yaml_id)
    except KeyError:
        # Not created yet, let's create it and add it to the index
        pass
    if yaml_data["type"] == "model":
        # need to special case model to avoid recursion
        if yaml_data["base"] == "json" or not code_model.options["models_mode"]:
            model_type = JSONModelType
        elif yaml_data["base"] == "dpg":
            model_type = DPGModelType  # type: ignore
        else:
            model_type = MsrestModelType  # type: ignore
        response = model_type(yaml_data, code_model)
        code_model.types_map[yaml_id] = response
        response.fill_instance_from_yaml(yaml_data, code_model)
    else:
        object_type = yaml_data.get("type")
        if object_type not in TYPE_TO_OBJECT:
            _LOGGER.warning(
                'Unrecognized definition type "%s" is found, falling back it as "string"! ',
                yaml_data["type"],
            )
            object_type = "string"
        response = TYPE_TO_OBJECT[object_type].from_yaml(yaml_data, code_model)  # type: ignore
    code_model.types_map[yaml_id] = response
    return response


RequestBuilderType = Union[RequestBuilder, OverloadedRequestBuilder]
ParameterType = Union[
    Parameter, RequestBuilderParameter, ClientParameter, ConfigParameter
]
OperationType = Union[Operation, LROOperation, PagingOperation, LROPagingOperation]
