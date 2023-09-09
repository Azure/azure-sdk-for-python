# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from abc import abstractmethod
from typing import (
    Optional,
    Any,
    Dict,
    TYPE_CHECKING,
    List,
    Generic,
    TypeVar,
    Union,
    cast,
)

from .imports import FileImport, ImportType, TypingSection
from .base import BaseType

if TYPE_CHECKING:
    from .code_model import CodeModel


class _CredentialPolicyBaseType:
    """Base class for our different credential policy types.

    Inherited by our BearerTokenCredentialPolicy and AzureKeyCredentialPolicy types.
    """

    def __init__(self, yaml_data: Dict[str, Any], code_model: "CodeModel") -> None:
        self.yaml_data = yaml_data
        self.code_model = code_model

    @abstractmethod
    def call(self, async_mode: bool) -> str:
        """
        How to call this credential policy. Used to initialize the credential policy in the config file.
        """


class BearerTokenCredentialPolicyType(_CredentialPolicyBaseType):
    """Credential policy type representing BearerTokenCredentialPolicy"""

    def __init__(
        self,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        credential_scopes: List[str],
    ) -> None:
        super().__init__(yaml_data, code_model)
        self.credential_scopes = credential_scopes

    def call(self, async_mode: bool) -> str:
        policy_name = f"{'Async' if async_mode else ''}BearerTokenCredentialPolicy"
        return f"policies.{policy_name}(self.credential, *self.credential_scopes, **kwargs)"

    @classmethod
    def from_yaml(
        cls, yaml_data: Dict[str, Any], code_model: "CodeModel"
    ) -> "BearerTokenCredentialPolicyType":
        return cls(yaml_data, code_model, yaml_data["credentialScopes"])


class ARMChallengeAuthenticationPolicyType(BearerTokenCredentialPolicyType):
    """Credential policy type representing ARMChallengeAuthenticationPolicy"""

    def call(self, async_mode: bool) -> str:
        policy_name = f"{'Async' if async_mode else ''}ARMChallengeAuthenticationPolicy"
        return f"{policy_name}(self.credential, *self.credential_scopes, **kwargs)"


class AzureKeyCredentialPolicyType(_CredentialPolicyBaseType):
    def __init__(
        self,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        key: str,
        scheme: Optional[str] = None,
    ) -> None:
        super().__init__(yaml_data, code_model)
        self.key = key
        self.scheme = scheme

    def call(self, async_mode: bool) -> str:
        params = f'"{self.key}", '
        if self.scheme:
            params += f'prefix="{self.scheme}", '
        return f"policies.AzureKeyCredentialPolicy(self.credential, {params}**kwargs)"

    @classmethod
    def from_yaml(
        cls, yaml_data: Dict[str, Any], code_model: "CodeModel"
    ) -> "AzureKeyCredentialPolicyType":
        return cls(
            yaml_data, code_model, yaml_data["key"], yaml_data.get("scheme", None)
        )


CredentialPolicyType = TypeVar(
    "CredentialPolicyType",
    bound=Union[
        BearerTokenCredentialPolicyType,
        ARMChallengeAuthenticationPolicyType,
        AzureKeyCredentialPolicyType,
    ],
)


class CredentialType(
    Generic[CredentialPolicyType], BaseType
):  # pylint:disable=abstract-method
    """Store info about the type of the credential. Can be either an AzureKeyCredential or a TokenCredential"""

    def __init__(
        self,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        policy: CredentialPolicyType,
    ) -> None:
        super().__init__(yaml_data, code_model)
        self.policy = policy

    def description(
        self, *, is_operation_file: bool  # pylint: disable=unused-argument
    ) -> str:
        return ""

    def get_json_template_representation(
        self,
        *,
        optional: bool = True,
        client_default_value_declaration: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Any:
        raise TypeError(
            "You should not try to get a JSON template representation of a CredentialSchema"
        )

    def docstring_text(self, **kwargs: Any) -> str:
        return "credential"

    @property
    def serialization_type(self) -> str:
        return self.docstring_type()

    @classmethod
    def from_yaml(
        cls, yaml_data: Dict[str, Any], code_model: "CodeModel"
    ) -> "CredentialType":
        from . import build_type

        return cls(
            yaml_data,
            code_model,
            policy=cast(
                CredentialPolicyType, build_type(yaml_data["policy"], code_model)
            ),
        )


class TokenCredentialType(
    CredentialType[  # pylint: disable=unsubscriptable-object
        Union[BearerTokenCredentialPolicyType, ARMChallengeAuthenticationPolicyType]
    ]
):
    """Type of a token credential. Used by BearerAuth and ARMChallenge policies"""

    def type_annotation(self, **kwargs: Any) -> str:
        if kwargs.get("async_mode"):
            return '"AsyncTokenCredential"'
        return '"TokenCredential"'

    @property
    def type_description(self) -> str:
        return "TokenCredential"

    def docstring_type(self, **kwargs: Any) -> str:
        if kwargs.get("async_mode"):
            return "~azure.core.credentials_async.AsyncTokenCredential"
        return "~azure.core.credentials.TokenCredential"

    def imports(self, **kwargs: Any) -> FileImport:
        file_import = FileImport()
        if kwargs.get("async_mode"):
            file_import.add_submodule_import(
                "azure.core.credentials_async",
                "AsyncTokenCredential",
                ImportType.AZURECORE,
                typing_section=TypingSection.TYPING,
            )
        else:
            file_import.add_submodule_import(
                "azure.core.credentials",
                "TokenCredential",
                ImportType.AZURECORE,
                typing_section=TypingSection.TYPING,
            )
        return file_import

    @property
    def instance_check_template(self) -> str:
        return "hasattr({}, 'get_token')"


class AzureKeyCredentialType(
    # pylint: disable=unsubscriptable-object
    CredentialType[AzureKeyCredentialPolicyType]
):
    """Type for an AzureKeyCredential"""

    def docstring_type(self, **kwargs: Any) -> str:  # pylint: disable=unused-argument
        return "~azure.core.credentials.AzureKeyCredential"

    def type_annotation(self, **kwargs: Any) -> str:  # pylint: disable=unused-argument
        return "AzureKeyCredential"

    @property
    def instance_check_template(self) -> str:
        return "isinstance({}, AzureKeyCredential)"

    def imports(self, **kwargs: Any) -> FileImport:  # pylint: disable=unused-argument
        file_import = FileImport()
        file_import.add_submodule_import(
            "azure.core.credentials",
            "AzureKeyCredential",
            ImportType.AZURECORE,
            typing_section=TypingSection.CONDITIONAL,
        )
        return file_import
