# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import List, Union

from marshmallow import Schema

from azure.ai.ml._internal._schema.component import NodeType
from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml._internal.entities.node import InternalBaseNode
from azure.ai.ml._schema import PathAwareSchema


class Scope(InternalBaseNode):
    """Node of scope components in pipeline with specific run settings."""

    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Scope, self).__init__(type=NodeType.SCOPE, **kwargs)
        self._init = True
        self._adla_account_name = kwargs.pop("adla_account_name", None)
        self._scope_param = kwargs.pop("scope_param", None)
        self._custom_job_name_suffix = kwargs.pop("custom_job_name_suffix", None)
        self._init = False

    @property
    def adla_account_name(self) -> str:
        """Get the ADLA account name for the scope."""
        return self._adla_account_name

    @adla_account_name.setter
    def adla_account_name(self, value: str):
        """Set the ADLA account name for the scope."""
        self._adla_account_name = value

    @property
    def scope_param(self) -> str:
        """Get the scope parameter for the scope."""
        return self._scope_param

    @scope_param.setter
    def scope_param(self, value: str):
        """Set the scope parameter for the scope."""
        self._scope_param = value

    @property
    def custom_job_name_suffix(self) -> str:
        """Get the custom job name suffix for the scope."""
        return self._custom_job_name_suffix

    @custom_job_name_suffix.setter
    def custom_job_name_suffix(self, value: str):
        """Set the custom job name suffix for the scope."""
        self._custom_job_name_suffix = value

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["custom_job_name_suffix", "scope_param", "adla_account_name"]

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.scope import ScopeSchema

        return ScopeSchema(context=context)


class ScopeComponent(InternalComponent):
    """Scope component.

    Override __call__ to enable strong type intelligence for scope
    specific run settings.
    """

    def __call__(self, *args, **kwargs) -> Scope:
        return super(InternalComponent, self).__call__(*args, **kwargs)
