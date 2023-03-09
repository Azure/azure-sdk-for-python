# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import List, Union

from marshmallow import Schema

from azure.ai.ml._internal._schema.component import NodeType
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
        self._priority = kwargs.pop("priority", None)
        self._init = False

    @property
    def adla_account_name(self) -> str:
        """The ADLA account name to use for the scope job."""
        return self._adla_account_name

    @adla_account_name.setter
    def adla_account_name(self, value: str):
        self._adla_account_name = value

    @property
    def scope_param(self) -> str:
        """nebula command used when submit the scope job."""
        return self._scope_param

    @scope_param.setter
    def scope_param(self, value: str):
        self._scope_param = value

    @property
    def custom_job_name_suffix(self) -> str:
        """Optional string to append to scope job name."""
        return self._custom_job_name_suffix

    @custom_job_name_suffix.setter
    def custom_job_name_suffix(self, value: str):
        self._custom_job_name_suffix = value

    @property
    def priority(self) -> int:
        """scope job priority.

        If set priority in scope_param, will override this setting.
        """
        return self._priority

    @priority.setter
    def priority(self, value: int):
        self._priority = value

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["custom_job_name_suffix", "scope_param", "adla_account_name", "priority"]

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.node import ScopeSchema

        return ScopeSchema(context=context)
