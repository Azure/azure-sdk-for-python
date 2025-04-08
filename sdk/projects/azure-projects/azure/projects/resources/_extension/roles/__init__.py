# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Dict, Generic, List, Literal, Mapping, Union, Optional
from typing_extensions import TypeVar, Self

from ..._identifiers import ResourceIdentifiers
from ...._resource import Resource, ResourceReference
from ...._bicep.utils import generate_name
from ...._bicep.expressions import Output, ResourceSymbol, RoleDefinition, Parameter
from ....resources.resourcegroup import ResourceGroup

if TYPE_CHECKING:
    from .types import RoleAssignmentResource


_DEFAULT_ROLE_ASSIGNMENT: "RoleAssignmentResource" = {}
RoleAssignmentResourceType = TypeVar(
    "RoleAssignmentResourceType", bound=Mapping[str, Any], default="RoleAssignmentResource"
)


class RoleAssignment(Resource, Generic[RoleAssignmentResourceType]):
    DEFAULTS: "RoleAssignmentResource" = _DEFAULT_ROLE_ASSIGNMENT  # type: ignore[assignment]
    properties: RoleAssignmentResourceType
    parent: None  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(self, properties: "RoleAssignmentResource", /, **kwargs) -> None:
        super().__init__(properties, identifier=ResourceIdentifiers.role_assignment, **kwargs)

    @property
    def resource(self) -> Literal["Microsoft.Authorization/roleAssignments"]:
        return "Microsoft.Authorization/roleAssignments"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    @classmethod
    def reference(
        cls,
        *,
        name: Optional[Union[str, Parameter]] = None,
        resource_group: Optional[Union[str, Parameter, "ResourceGroup[ResourceReference]"]] = None,
        subscription: Optional[Union[str, Parameter]] = None,
        parent: Optional[Resource] = None,
    ) -> Self:
        raise TypeError("Referenced Role Assignments not supported.")

    def _outputs(self, **kwargs) -> Dict[str, List[Output]]:
        return {}

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        if suffix:
            resource_ref = f"roleassignment_{generate_name(suffix)}"
        else:
            resource_ref = "roleassignment"
        return ResourceSymbol(resource_ref)


BUILT_IN_ROLES: Dict[str, RoleDefinition] = {
    "Contributor": RoleDefinition("b24988ac-6180-42a0-ab88-20f7382dd24c"),
    "Owner": RoleDefinition("8e3af657-a8ff-443c-a75c-2fe8c4bcb635"),
    "Reader": RoleDefinition("acdd72a7-3385-48ef-bd42-f606fba81ae7"),
    "Reader and Data Access": RoleDefinition("c12c1c16-33a1-487b-954d-41c89c60f349"),
    "Role Based Access Control Administrator": RoleDefinition("f58310d9-a9f6-439a-9e8d-f62e7b41a168"),
    "User Access Administrator": RoleDefinition("18d7d88d-d35e-4fb5-a5c3-7773c20a72d9"),
    "Storage Account Backup Contributor": RoleDefinition("e5e2a7ff-d759-4cd2-bb51-3152d37e2eb1"),
    "Storage Account Contributor": RoleDefinition("17d1049b-9a84-46fb-8f53-869881c3d3ab"),
    "Storage Account Key Operator Service Role": RoleDefinition("81a9662b-bebf-436f-a333-f67b29880f12"),
    "Storage Blob Data Contributor": RoleDefinition("ba92f5b4-2d11-453d-a403-e96b0029c9fe"),
    "Storage Blob Data Owner": RoleDefinition("b7e6dc6d-f1e8-4753-8033-0f276bb0955b"),
    "Storage Blob Data Reader": RoleDefinition("2a2b9908-6ea1-4ae2-8e65-a410df84e7d1"),
    "Storage Blob Delegator": RoleDefinition("db58b8e5-c6ad-4a2a-8342-4190687cbf4a"),
    "Storage File Data Privileged Contributor": RoleDefinition("69566ab7-960f-475b-8e7c-b3118f30c6bd"),
    "Storage File Data Privileged Reader": RoleDefinition("b8eda974-7b85-4f76-af95-65846b26df6d"),
    "Storage File Data SMB Share Contributor": RoleDefinition("0c867c2a-1d8c-454a-a3db-ab2ea1bdc8bb"),
    "Storage File Data SMB Share Elevated Contributor": RoleDefinition("a7264617-510b-434b-a828-9731dc254ea7"),
    "Storage File Data SMB Share Reader": RoleDefinition("aba4ae5f-2193-4029-9191-0cb91df5e314"),
    "Storage Queue Data Contributor": RoleDefinition("974c5e8b-45b9-4653-ba55-5f855dd0fb88"),
    "Storage Queue Data Message Processor": RoleDefinition("8a0f0c08-91a1-4084-bc3d-661d67233fed"),
    "Storage Queue Data Message Sender": RoleDefinition("c6a89b2d-59bc-44d0-9896-0f6e12d7b80a"),
    "Storage Queue Data Reader": RoleDefinition("19e7f393-937e-4f77-808e-94535e297925"),
    "Storage Table Data Contributor": RoleDefinition("0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3"),
    "Storage Table Data Reader": RoleDefinition("76199698-9eea-4c19-bc75-cec21354c6b6"),
    "Cognitive Services Contributor": RoleDefinition("25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68"),
    "Cognitive Services Custom Vision Contributor": RoleDefinition("c1ff6cc2-c111-46fe-8896-e0ef812ad9f3"),
    "Cognitive Services Custom Vision Deployment": RoleDefinition("5c4089e1-6d96-4d2f-b296-c1bc7137275f"),
    "Cognitive Services Custom Vision Labeler": RoleDefinition("88424f51-ebe7-446f-bc41-7fa16989e96c"),
    "Cognitive Services Custom Vision Reader": RoleDefinition("93586559-c37d-4a6b-ba08-b9f0940c2d73"),
    "Cognitive Services Custom Vision Trainer": RoleDefinition("0a5ae4ab-0d65-4eeb-be61-29fc9b54394b"),
    "Cognitive Services Data Reader": RoleDefinition("b59867f0-fa02-499b-be73-45a86b5b3e1c"),
    "Cognitive Services Face Recognizer": RoleDefinition("9894cab4-e18a-44aa-828b-cb588cd6f2d7"),
    "Cognitive Services Immersive Reader User": RoleDefinition("b2de6794-95db-4659-8781-7e080d3f2b9d"),
    "Cognitive Services Language Owner": RoleDefinition("f07febfe-79bc-46b1-8b37-790e26e6e498"),
    "Cognitive Services Language Reader": RoleDefinition("7628b7b8-a8b2-4cdc-b46f-e9b35248918e"),
    "Cognitive Services Language Writer": RoleDefinition("f2310ca1-dc64-4889-bb49-c8e0fa3d47a8"),
    "Cognitive Services LUIS Owner": RoleDefinition("f72c8140-2111-481c-87ff-72b910f6e3f8"),
    "Cognitive Services LUIS Reader": RoleDefinition("18e81cdc-4e98-4e29-a639-e7d10c5a6226"),
    "Cognitive Services LUIS Writer": RoleDefinition("6322a993-d5c9-4bed-b113-e49bbea25b27"),
    "Cognitive Services Metrics Advisor Administrator": RoleDefinition("cb43c632-a144-4ec5-977c-e80c4affc34a"),
    "Cognitive Services Metrics Advisor User": RoleDefinition("3b20f47b-3825-43cb-8114-4bd2201156a8"),
    "Cognitive Services OpenAI Contributor": RoleDefinition("a001fd3d-188f-4b5d-821b-7da978bf7442"),
    "Cognitive Services OpenAI User": RoleDefinition("5e0bd9bd-7b93-4f28-af87-19fc36ad61bd"),
    "Cognitive Services QnA Maker Editor": RoleDefinition("f4cc2bf9-21be-47a1-bdf1-5c5804381025"),
    "Cognitive Services QnA Maker Reader": RoleDefinition("466ccd10-b268-4a11-b098-b4849f024126"),
    "Cognitive Services Speech Contributor": RoleDefinition("0e75ca1e-0464-4b4d-8b93-68208a576181"),
    "Cognitive Services Speech User": RoleDefinition("f2dc8367-1007-4938-bd23-fe263f013447"),
    "Cognitive Services User": RoleDefinition("a97b65f3-24c7-4388-baec-2e87135dc908"),
    "Key Vault Administrator": RoleDefinition("00482a5a-887f-4fb3-b363-3b7fe8e74483"),
    "Key Vault Certificates Officer": RoleDefinition("a4417e6f-fecd-4de8-b567-7b0420556985"),
    "Key Vault Certificate User": RoleDefinition("db79e9a7-68ee-4b58-9aeb-b90e7c24fcba"),
    "Key Vault Contributor": RoleDefinition("f25e0fa2-a7c8-4377-a976-54943a77a395"),
    "Key Vault Crypto Officer": RoleDefinition("14b46e9e-c2b7-41b4-b07b-48a6ebf60603"),
    "Key Vault Crypto Service Encryption User": RoleDefinition("e147488a-f6f5-4113-8e2d-b22465e65bf6"),
    "Key Vault Crypto User": RoleDefinition("12338af0-0e69-4776-bea7-57ae8d297424"),
    "Key Vault Reader": RoleDefinition("21090545-7ca7-4776-b22c-e363652d74d2"),
    "Key Vault Secrets Officer": RoleDefinition("b86a8fe4-44ce-4948-aee5-eccb2c155cd7"),
    "Key Vault Secrets User": RoleDefinition("4633458b-17de-408a-b874-0445c86b69e6"),
    "Search Index Data Contributor": RoleDefinition("8ebe5a00-799e-43f5-93ac-243d3dce84a7"),
    "Search Index Data Reader": RoleDefinition("1407120a-92aa-4202-b7e9-c0e197c71c8f"),
    "Search Service Contributor": RoleDefinition("7ca78c08-252a-4471-8644-bb5ff32d4ba0"),
    "App Compliance Automation Administrator": RoleDefinition("0f37683f-2463-46b6-9ce7-9b788b988ba2"),
    "App Compliance Automation Reader": RoleDefinition("ffc6bbe0-e443-4c3b-bf54-26581bb2f78e"),
    "App Configuration Contributor": RoleDefinition("fe86443c-f201-4fc4-9d2a-ac61149fbda0"),
    "App Configuration Data Owner": RoleDefinition("5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b"),
    "App Configuration Data Reader": RoleDefinition("516239f1-63e1-4d78-a4de-a74fb236a071"),
    "App Configuration Reader": RoleDefinition("175b81b9-6e0d-490a-85e4-0d422273c10c"),
}
