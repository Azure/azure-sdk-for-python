# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from abc import ABC

from azure.ai.ml._restclient.v2022_06_01_preview.models import AmlToken as RestAmlToken
from azure.ai.ml._restclient.v2022_06_01_preview.models import IdentityConfiguration, IdentityConfigurationType
from azure.ai.ml._restclient.v2022_06_01_preview.models import ManagedIdentity as RestManagedIdentity
from azure.ai.ml._restclient.v2022_06_01_preview.models import UserIdentity as RestUserIdentity
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, JobException

module_logger = logging.getLogger(__name__)


class Identity(ABC, RestTranslatableMixin):
    def __init__(self):
        self.type = None

    @classmethod
    def _from_rest_object(cls, obj: IdentityConfiguration) -> "Identity":
        mapping = {
            IdentityConfigurationType.AML_TOKEN: AmlToken,
            IdentityConfigurationType.MANAGED: ManagedIdentity,
            IdentityConfigurationType.USER_IDENTITY: UserIdentity,
        }

        identity_class = mapping.get(obj.identity_type, None)
        if identity_class:
            return identity_class._from_rest_object(obj)
        else:
            msg = f"Unknown identity type: {obj.identity_type}"
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.IDENTITY,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identity):
            return NotImplemented
        return self._to_rest_object() == other._to_rest_object()


class AmlToken(Identity):
    """AML Token identity configuration."""

    def __init__(self):
        self.type = camel_to_snake(IdentityConfigurationType.AML_TOKEN)

    def _to_rest_object(self) -> RestAmlToken:
        return RestAmlToken()

    @classmethod
    # pylint: disable=unused-argument
    def _from_rest_object(cls, obj: RestAmlToken) -> "AmlToken":
        return cls()


class ManagedIdentity(Identity):
    """Managed identity configuration.

    :param client_id: Specifies a user-assigned identity by client ID. For system-assigned, do not
     set this field.
    :type client_id: str
    :param object_id: Specifies a user-assigned identity by object ID. For system-assigned, do not
     set this field.
    :type object_id: str
    :param msi_resource_id: Specifies a user-assigned identity by ARM resource ID. For system-assigned,
     do not set this field.
    :type msi_resource_id: str
    """

    def __init__(
        self,
        *,
        client_id: str = None,
        object_id: str = None,
        msi_resource_id: str = None,
    ):
        self.type = camel_to_snake(IdentityConfigurationType.MANAGED)
        self.client_id = client_id
        self.object_id = object_id
        self.msi_resource_id = msi_resource_id

    def _to_rest_object(self) -> RestManagedIdentity:
        return RestManagedIdentity(
            client_id=self.client_id,
            object_id=self.object_id,
            resource_id=self.msi_resource_id,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestManagedIdentity) -> "ManagedIdentity":
        return cls(
            client_id=obj.client_id,
            object_id=obj.client_id,
            msi_resource_id=obj.resource_id,
        )


class UserIdentity(Identity):
    """User identity configuration."""

    def __init__(self):
        self.type = camel_to_snake(IdentityConfigurationType.USER_IDENTITY)

    def _to_rest_object(self) -> RestUserIdentity:
        return RestUserIdentity()

    @classmethod
    # pylint: disable=unused-argument
    def _from_rest_object(cls, obj: RestUserIdentity) -> "UserIdentity":
        return cls()
